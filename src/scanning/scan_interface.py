# External
import requests
from flask import Flask, request
from flask_cors import CORS 
from Crypto.Hash import SHA256

# Local
import net_tools as nt
from config import Config
from loading_bar import Loading_bar
from threadpool import Threadpool

# Stdlib
import logging
import json, sys
import threading
from functools import wraps
import json
import time

# Total number of threads spawned for the threadpool
NUM_THREADS = 50

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

tp = Threadpool(NUM_THREADS)
daemon_sleep = threading.Event()
daemon_sleep.set()
daemon_running = False
daemon_network_id = -1
daemon_auth_token = ""

loading_bars = dict()
daemon_clients = set()
pending_daemon_clients = set()

DB_SERVER_URL = "http://" + app.config["POSTGRES_URI"]

# Number of seconds between a scan ending and a new one starting in daemon mode.
daemon_scan_rate = 60

# The default settings that a new user gets
default_settings = {
    "TCP"                     : True,
    "UDP"                     : True, 
    "ports"                   : [22,23,80,443],
    "run_ports"               : True,
    "run_os"                  : False,
    "run_hostname"            : True,
    "run_mac_vendor"          : True,
    "run_trace"               : True,
    "run_vertical_trace"      : True,
    "defaultView"             : "grid",
    "defaultNodeColour"       : "0FF54A",
    "defaultEdgeColour"       : "32FFAB",
    "defaultBackgroundColour" : "320000"
}

daemon_settings = default_settings


def create_response(message, code, content=""):

    return {"message" : message, "status" : code, "content" : content}, code


# Authentication wrapper
def require_auth(func):

    # Ensures that there is a valid authentication token attached to each request.
    @wraps(func)
    def decorated(*args, **kwargs):
        
        # auth = None
        # if "Auth-Token" in request.headers:
        #     auth = request.headers["Auth-Token"]
        # else:
        #     return create_response("Authentication token not in request headers.", 401)
        
        # # Run the decorated function
        # return func(auth, *args, **kwargs)
        return func("auf", *args, **kwargs)
    
    return decorated


# Retrieves a given user's settings from the database, adds them if they are non existent
def get_settings(auth, daemon=False):

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

    loading_bars[auth] = Loading_bar()

    # Initialises network
    network = nt.init_scan(network_id)
    # Retrieves devices
    nt.add_devices(network, tp, loading_bars[auth])
    # Runs basic traceroute
    nt.add_routes(network, tp, loading_bars[auth])
    # Saves to database
    res = requests.put(DB_SERVER_URL + "/networks/add", json=network.to_json(), headers={"Auth-Token" : auth})
    if res.status_code != 200:
        print(auth)
        print(f"[ERR ] Failed to write network to database.\n\t [{res.status_code}]: {res.content.decode('utf-8')}")
        del loading_bars[auth]
        return

    network_id = json.loads(res.content.decode("utf-8"))["content"]
    network.network_id = network_id

    scans = [
        {"setting" : "run_vertical_trace", "func" : nt.vertical_traceroute, "args" : [network]},
        {"setting" : "run_mac_vendor",     "func" : nt.add_mac_vendors,     "args" : [network, loading_bars[auth]]},
        {"setting" : "run_website_status", "func" : nt.add_website_status,  "args" : [network, tp, loading_bars[auth]]},
        {"setting" : "run_hostname",       "func" : nt.add_hostnames,       "args" : [network, tp, loading_bars[auth]]},
        {"setting" : "run_os",             "func" : nt.add_os_info,         "args" : [network, tp, loading_bars[auth]]},
        {"setting" : "run_ports",          "func" : nt.add_ports,           "args" : [network, tp, loading_bars[auth], settings["ports"]]},
    ]

    for scan in scans:
        if scan["setting"] in settings.keys() and settings[scan["setting"]]:
            scan["func"](*scan["args"])
            res = requests.put(DB_SERVER_URL + "/networks/update", json=network.to_json(), headers={"Auth-Token" : auth})
            if res.status_code != 200:
                print(f"[ERR ] Failed to write network to database.\n\t [{res.status_code}]: {res.content.decode('utf-8')}")
                del loading_bars[auth]
                return

    print(f"[INFO] Successfully scanned network '{network.name}', added to database.")
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
        return create_response("Malformed settings, automatic reset has failed. Please contact system administrator.", 500)

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

    global daemon_running, daemon_network_id, daemon_sleep, daemon_scan_rate
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
    print("[INFO] Daemon started scanning %d..." % network_id)
    return create_response("Success", 200)


@app.post("/daemon/end")
@require_auth
def end_daemon(auth):

    global daemon_running, daemon_network_id, daemon_sleep
    if daemon_running:
        daemon_running = False
        daemon_sleep.clear()
        print("[INFO] Daemon stopping after current scan...")
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
        return create_response("success", 200, content=loading_bars[daemon_auth_token].get_progress())
    
    return create_response("Scan finished.", 200, content={"label" : "", "total" : 0, "progress" : 0})


@app.get("/progress")
@require_auth
def get_progress(auth):

    if auth in loading_bars.keys():
        return create_response("success", 200, content=loading_bars[auth].get_progress())
    
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

    print("[INFO] Daemon is starting!")

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
            print("[INFO] Daemon is waiting...")
            daemon_sleep.clear()
            daemon_sleep.wait()

        # create new network id if doesnt exist, then save to that id just for the daemon account
        run_scan(daemon_network_id, daemon_settings, token)

        # Waits configurable amount of time before scanning again
        time.sleep(daemon_scan_rate)


if __name__ == "__main__":

    daemon_thread = threading.Thread(target=run_daemon)
    daemon_thread.daemon = True
    daemon_thread.start()
    app.run(host=app.config["SERVER_HOST"], port=app.config["SERVER_PORT"])