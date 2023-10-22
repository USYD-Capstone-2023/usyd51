# External
import requests
from flask import Flask, request
from flask_cors import CORS 
from Crypto.Hash import SHA256

# Local
from net_tools import NetTools
from config import Config
from loading_bar import LoadingBar, ProgressUI
from threadpoolAttr import ThreadpoolAttr

# Stdlib
import logging, json, sys, threading, time
from functools import wraps

# # Hides flask output logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# Load the configuration from the specified config class
app.config.from_object(Config)

# Define the app configuration based on command line args
if len(sys.argv) < 2:
    print("Please enter either 'remote' or 'local'")
    sys.exit(-1)

if sys.argv[1] == "remote":
    app.config.from_object("config.RemoteConfig")

elif sys.argv[1] == "local":
    app.config.from_object("config.LocalConfig")

elif sys.argv[1] == "testing":
    app.config.from_object("config.TestingConfig")

elif sys.argv[1] == "docker-local":
    app.config.from_object("config.DockerLocalConfig")

else:
    print("Please enter either 'remote' or 'local'")
    sys.exit(-1)


CORS(app, allow_headers=["Content-Type", "Auth-Token", "Access-Control-Allow-Credentials"],
    expose_headers="Auth-Token")

daemon_sleep = threading.Event()
daemon_sleep.set()
daemon_running = False
daemon_network_id = -1
daemon_auth_token = ""

loading_bars = dict()
daemon_clients = set()
pending_daemon_clients = set()

DB_SERVER_URL = "http://" + app.config["POSTGRES_URI"]

# Creates a new instance of the scanning tool suite with 50 threads
nt = NetTools(50)

# Number of seconds between a scan ending and a new one starting in daemon mode.
daemon_scan_rate = 60

# Settings for daemon scans, fills in from remote db when running
daemon_settings = {}

ui = ProgressUI(40)


def create_response(message, code, content=""):

    return {"message" : message, "status" : code, "content" : content}, code


def update_network(network, auth):
    res = requests.put(DB_SERVER_URL + "/networks/update", json=network.to_json(), headers={"Auth-Token" : auth})
    if res.status_code != 200:
        print(f"[ERR ] Failed to write network to database.\n\t [{res.status_code}]: {res.content.decode('utf-8')}")
        del loading_bars[auth]
        return res

    return True


# Authentication wrapper
def require_auth(func):
    # Ensures that there is a valid authentication token attached to each request.
    @wraps(func)
    def decorated(*args, **kwargs):
        
        auth = None
        if "Auth-Token" in request.headers:
            auth = request.headers["Auth-Token"]
        else:
            return create_response("Authentication token not in request headers.", 401)
        
        # Run the decorated function
        return func(auth, *args, **kwargs)
    
    return decorated


# Retrieves a given user's settings from the database, adds them if they are non existent
def get_settings(auth, daemon=False):

    print()
    res = requests.get(DB_SERVER_URL + "/settings", headers={"Auth-Token" : auth})
    if res.status_code != 200:
        return None

    settings = json.loads(res.content.decode("utf-8"))["content"]

    if daemon:
        return {
            "TCP"                : settings["daemon_TCP"],
            "UDP"                : settings["daemon_UDP"], 
            "ports"              : settings["daemon_ports"],
            "run_ports"          : settings["daemon_run_ports"],
            "run_os"             : settings["daemon_run_os"],
            "run_hostname"       : settings["daemon_run_hostname"],
            "run_mac_vendor"     : settings["daemon_run_mac_vendor"],
            "run_trace"          : settings["daemon_run_trace"],
            "run_vertical_trace" : settings["daemon_run_vertical_trace"],
            "run_website_status" : settings["daemon_run_website_status"],
            }, settings["daemon_scan_rate"]

    return settings


# Checks if a given network ID is valid and numeric
def validate_network_id(network_id):

    if network_id.isnumeric() or network_id == "-1":
        return int(network_id)
    else:
        return None
    

# Runs a network scan on the given network with the given settings arguments.
# Automatically saves network to database on completion.
def run_scan(network_id, settings, auth):

    global loading_bars

    lb_map = {"run_vertical_trace" : "vertical_traceroute",
              "run_mac_vendor"     : "MAC_vendors",
              "run_website_status" : "website_hosting_scan",
              "run_hostname"       : "hostname_resolution",
              "run_os"             : "os_scan",
              "run_ports"          : "port_scan"}

    bars = {"ARP_scan"             : LoadingBar("ARP_scan", -1),
            "traceroute"           : LoadingBar("traceroute", -1)}
    
    for setting in lb_map.keys():
        if setting in settings.keys() and settings[setting]:
            bars[lb_map[setting]] = LoadingBar(lb_map[setting], -1)

    loading_bars[auth] = bars
    ui.add_bars(auth, bars)

    # Initialises network
    network = nt.init_scan(network_id)

    # Retrieves devices
    nt.add_devices(network, bars["ARP_scan"])
    bars["traceroute"].set_total(len(network.devices))

    # Runs basic traceroute
    nt.add_routes(network, bars["traceroute"])

    if "run_vertical_trace" in settings.keys() and settings["run_vertical_trace"]:
        bars["vertical_traceroute"].set_total(1)
        nt.vertical_traceroute(network)
        bars["vertical_traceroute"].set_progress(1)

    for lb in bars.values():
        if lb.label in ["ARP_scan", "traceroute", "vertical_traceroute"]:
            continue

        lb.set_total(len(network.devices))

    # Saves to database
    res = requests.put(DB_SERVER_URL + "/networks/add", json=network.to_json(), headers={"Auth-Token" : auth})
    if res.status_code != 200:
        print(f"[ERR ] Failed to write network to database.\n\t [{res.status_code}]: {res.content.decode('utf-8')}")
        ui.rm_bars(auth)
        del loading_bars[auth]
        return

    network_id = json.loads(res.content.decode("utf-8"))["content"]
    network.network_id = network_id

    if "run_mac_vendor" in settings.keys() and settings["run_mac_vendor"]:
        nt.add_mac_vendors(network, bars["MAC_vendors"])
        res = update_network(network, auth)
        if res != True:
            ui.rm_bars(auth)
            del loading_bars[auth]
            return res

    parallel_scans = [
        {"setting"      : "run_website_status",
         "func"         : nt.dispatch_website_scan,
         "args"         : [network],
         "update_func"  : nt.update_website_status,
         "lb"           : None if "website_hosting_scan" not in bars.keys() else bars["website_hosting_scan"]},

        {"setting"      : "run_hostname",
         "func"         : nt.dispatch_hostname_scan,
         "args"         : [network],
         "update_func"  : nt.update_hostnames,
         "lb"           : None if "hostname_resolution" not in bars.keys() else bars["hostname_resolution"]},

        {"setting"      : "run_os",
         "func"         : nt.dispatch_os_scan,
         "args"         : [network],
         "update_func"  : nt.update_os,
         "lb"           : None if "os_scan" not in bars.keys() else bars["os_scan"]},

        {"setting"      : "run_ports",
         "func"         : nt.dispatch_port_scan,
         "args"         : [network, settings["ports"]],
         "update_func"  : nt.update_ports,
         "lb"           : None if "port_scan" not in bars.keys() else bars["port_scan"]},
    ]
    
    thread_attrs = {}
    for scan in parallel_scans:
        if scan["setting"] in settings.keys() and settings[scan["setting"]]:
            thread_attrs[scan["setting"]] = ThreadpoolAttr(len(network.devices), scan["update_func"], scan["lb"])
            scan["func"](*scan["args"], thread_attrs[scan["setting"]])

    while True:
        
        done = True
        for scan_attr in thread_attrs.values():
            if not scan_attr.batch_done:
                done = False
                # Updates loading bar progress
                scan_attr.mutex.acquire()
                if scan_attr.ctr[0] != scan_attr.lb.progress:
                    scan_attr.lb.set_progress(scan_attr.ctr[0])
                    if scan_attr.lb.progress == scan_attr.lb.total_value:
                        scan_attr.batch_done = True

                scan_attr.mutex.release()

                if scan_attr.batch_done:
                    scan_attr.update_func(network, scan_attr.ret)
                    res = update_network(network, auth)
                    if res != True:
                        ui.rm_bars(auth)
                        del loading_bars[auth]
                        return res
        
        if done:
            break

        time.sleep(0.1)

    ui.rm_bars(auth)
    del loading_bars[auth]
    return network


def verify_current_connection(network_id, auth):

    if network_id == -1:
        return create_response("Valid", 200)

    network = requests.get(DB_SERVER_URL + "/networks/%s" % (network_id), headers={"Auth-Token" : auth})
    
    # Network hasnt been created, so user is trivially connected to the network
    if network.status_code == 500:
        return create_response("Valid", 200)
    
    # Not authorised for this network, or some other database error code
    if network.status_code != 200:
        return network.content.decode("utf8"), network.status_code

    network = json.loads(network.content.decode("utf-8"))["content"]

    # Check that the network being scanned corresponds to the one in the database
    gateway_mac = nt.get_gateway_mac()
    if "gateway_mac" not in network.keys() or network["gateway_mac"] != gateway_mac:
        return create_response("Not currently connected to the requested network.", 500)
    
    # Connected to the requested network
    return create_response("Valid", 200)


# Finds all devices on the network, runs all scans outlined in users settings
# If a valid network id is entered, it will add the scan results to the database under that ID with a new timestamp,
# otherwise will create a new network in the db
@app.post("/scan/<network_id>")
@require_auth
def scan_network(auth, network_id):

    # Checks that the entered network id is valid
    network_id = validate_network_id(network_id)
    if network_id == None:
        return create_response("Invalid network ID entered.", 500)
    
    # Checks that the user is connected to the network they are trying to scan
    res = verify_current_connection(network_id, auth)
    if res[1] != 200:
        return res[0], res[1]
    
    # Retrieves users scanning preferences
    settings = get_settings(auth)
    if settings == None:
        return create_response("Invalid scan settings retrieved from database, possible version mismatch. Aborting...", 500)

    # Checks if user is already running a scan
    if auth in loading_bars.keys():
        return create_response("User is already running a scan.", 500)


    # Dispatches scan
    scan_thread = threading.Thread(target=run_scan, args=(network_id, settings, auth))
    scan_thread.daemon = True
    scan_thread.start()
    return create_response("Scan has started.", 200)


@app.post("/daemon/start/<network_id>")
@require_auth
def start_daemon(auth, network_id):

    global daemon_running, daemon_network_id, daemon_sleep, daemon_scan_rate, daemon_settings
    # Checks that the entered network id is valid
    network_id = validate_network_id(network_id)
    if network_id == None:
        return create_response("Invalid network ID entered.", 500)

    if daemon_running:
        return create_response("Daemon already running.", 500)

    daemon_settings = get_settings(auth, daemon=True)
    daemon_scan_rate = daemon_settings[1]
    daemon_settings = daemon_settings[0]
    daemon_network_id = network_id
    daemon_running = True
    daemon_sleep.set()
    return create_response("Success", 200)


@app.post("/daemon/end")
@require_auth
def end_daemon(auth):

    global daemon_running, daemon_network_id, daemon_sleep
    if daemon_running:
        daemon_running = False
        daemon_sleep.clear()
        return create_response("Success", 200)
    
    return create_response("Daemon not running", 500)


@app.post("/daemon/new")
@require_auth
def init_daemon_network(auth):

    global daemon_auth_token, daemon_scan_rate
    daemon_auth_token = daemon_get_auth()

    # Checks if user is already running a scan
    if daemon_auth_token in loading_bars.keys():
        return create_response("User is already running a scan.", 500)

    daemon_settings = get_settings(auth, daemon=True)
    daemon_scan_rate = daemon_settings[1]
    daemon_settings = daemon_settings[0]
    
    # Dispatches scan
    scan_thread = threading.Thread(target=run_scan, args=(-1, daemon_settings, daemon_auth_token))
    scan_thread.daemon = True
    scan_thread.start()
    return create_response("Scan has started.", 200)


@app.get("/daemon/progress")
@require_auth
def get_daemon_progress(auth):

    global daemon_auth_token
    if daemon_auth_token in loading_bars.keys():
        return create_response("success", 200, content={x.label : x.to_json() for x in loading_bars[daemon_auth_token].values()})
    
    return create_response("Scan finished.", 200, content={"label" : "", "total" : 0, "progress" : 0})


@app.get("/progress")
@require_auth
def get_progress(auth):

    global loading_bars
    if auth in loading_bars.keys():
        return create_response("success", 200, content={x.label : x.to_json() for x in loading_bars[auth].values()})
    
    return create_response("Scan finished.", 200, content={"label" : "", "total" : 0, "progress" : 0})


# Serves the information of the dhcp server
@app.get("/dhcp")
def get_dhcp_server_info():

    return create_response("success", 200, content=nt.get_dhcp_server_info())


@app.get("/ssid")
def get_current_ssid():

    return create_response("success", 200, nt.get_ssid())


def daemon_get_auth():
    # Retrieve salt
    res = requests.get(DB_SERVER_URL + "/users/daemon/salt")
    if res.status_code != 200:
        return None

    content = json.loads(res.content)
    salt = content["content"]["salt"]
    hash = SHA256.new()
    hash.update(bytes("password" + salt, "utf-8"))

    # Retrieve auth token each scan, as token expires after set time and needs to be refreshed
    res = requests.post(DB_SERVER_URL + "/login", json={"username" : "daemon", "password" : str(hash.hexdigest())})
    if res.status_code != 200:
        return None

    content = json.loads(res.content)
    return content["content"]["Auth-Token"]


# Starts the scanning daemon for the network that this server is connected to
def run_daemon():

    while True:
        token = daemon_get_auth()
        if not token:
            count = 0
            total = 5
            while count <= total:
                sys.stdout.write("[ERR ] Failed to connect to remote server, retrying in %d seconds... \r" % (total - count))
                time.sleep(1)
                count += 1

            sys.stdout.write("\n")
            continue

        # Sleeps until there is a client to scan for
        if not daemon_running:
            daemon_sleep.clear()
            daemon_sleep.wait()

        # create new network id if doesnt exist, then save to that id just for the daemon account
        run_scan(daemon_network_id, daemon_settings, token)

        # Waits configurable amount of time before scanning again
        time.sleep(daemon_scan_rate)

def run_ui():

    while True:
        ui.show()
        time.sleep(0.1)


if __name__ == "__main__":

    daemon_thread = threading.Thread(target=run_daemon)
    daemon_thread.daemon = True
    daemon_thread.start()

    ui_thread = threading.Thread(target=run_ui)
    ui_thread.daemon = True
    ui_thread.start()
    app.run(host=app.config["SERVER_HOST"], port=app.config["SERVER_PORT"])