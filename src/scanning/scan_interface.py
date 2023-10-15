# External
import requests
from flask import Flask, request
from flask_cors import CORS 
from loading_bar import Loading_bar
from threadpool import Threadpool
import threading
from functools import wraps
import json
import time
from Crypto.Hash import SHA256
import logging

# Local
import net_tools as nt

# Stdlib
import json, sys

# Total number of threads spawned for the threadpool
NUM_THREADS = 50

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
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

# Number of seconds between a scan ending and a new one starting in daemon mode.
daemon_scan_rate = 60

# The default settings that a new user gets
default_settings = {
    "TCP" : True,
    "UDP" : True, 
    "ports": [22,23,80,443],
    "run_ports": True,
    "run_os": False,
    "run_hostname": True,
    "run_mac_vendor": True,
    "run_trace": True,
    "run_vertical_trace": True,
    "defaultView": "grid",
    "defaultNodeColour": "0FF54A",
    "defaultEdgeColour": "32FFAB",
    "defaultBackgroundColour": "320000"
}


def create_response(message, code, content=""):

    return {"message" : message, "status" : code, "content" : content}, code


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
def get_settings(auth):

    res = requests.get(DB_SERVER_URL + "/settings", headers={"Auth-Token" : auth})

    if res.status_code_code != 200:
        return None

    settings = json.loads(res.content.decode("utf-8"))["content"]
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
    if res.status_code_code != 200:
        print(f"[ERR ] Failed to write network to database.\n\t [{res.status_code_code}]: {res.content.decode('utf-8')}")
        del loading_bars[auth]
        return

    network_id = json.loads(res.content.decode("utf-8"))["content"]
    network.network_id = network_id

    scans = [
        {"setting" : "run_vertical_trace", "func" : nt.vertical_traceroute, "args" : [network]},
        {"setting" : "run_mac_vendor",     "func" : nt.add_mac_vendors,     "args" : [network, loading_bars[auth]]},
        {"setting" : "run_hostname",       "func" : nt.add_hostnames,       "args" : [network, tp, loading_bars[auth]]},
        {"setting" : "run_os",             "func" : nt.add_os_info,         "args" : [network, tp, loading_bars[auth]]},
        {"setting" : "run_ports",          "func" : nt.add_ports,           "args" : [network, tp, loading_bars[auth], settings["ports"]]},
    ]

    for scan in scans:
        if settings[scan["setting"]]:
            scan["func"](*scan["args"])
            res = requests.put(DB_SERVER_URL + "/networks/update", json=network.to_json(), headers={"Auth-Token" : auth})
            if res.status_code_code != 200:
                print(f"[ERR ] Failed to write network to database.\n\t [{res.status_code_code}]: {res.content.decode('utf-8')}")
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
    if network.status_code_code == 500:
        return create_response("Valid", 200)
    
    # Not authorised for this network, or some other database error code
    if network.status_code_code != 200:
        return network.content.decode("utf8"), network.status_code_code

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
    

# Starts an automatic scanning daemon on the network specified.
# Scans are conducted at the interval specified in the user's settings table (NOT IMPLEMENTED, HARDCODED ABOVE CURRENTLY)
# The daemon will be shutdown after the end_daemon method is called, or if it encounters a specific number of 
# consecutive database faults.
@app.post("/daemon/register")
@require_auth
def register_daemon_client(auth):

    res = requests.post(f"{DB_SERVER_URL}/users/id", headers={"Auth-Token" : auth})
    if res.status_code != 200:
        return res
    
    user_id = json.loads(res.content)

    if user_id in daemon_clients:
        return create_response("User is already registered with scanning daemon.", 500)
    
    daemon_auth_token = daemon_get_auth()
    if daemon_auth_token == None:
        return create_response("Failed to retrieve daemon authentication token. Try again.", 500)
    
    daemon_clients.add(user_id)
    res = requests.post(f"{DB_SERVER_URL}/users/{daemon_network_id}/share/{user_id}", headers={"Auth-Token" : daemon_auth_token})
    if res.status_code != 200:
        return res

    daemon_sleep.clear()
    return create_response("Success", 200)


@app.post("/daemon/start/<network_id>")
@require_auth
def start_daemon(auth, network_id):

    if daemon_running:
        return create_response("Daemon already running.", 500)
    
    res = requests.post(f"{DB_SERVER_URL}/users/{network_id}/share/0", headers={"Auth-Token" : auth})
    if res.status_code != 200:
        return res
    
    daemon_network_id = network_id
    daemon_running = True
    daemon_sleep.clear()
    return create_response("Success", 500)


# Sets the flag to kill the scanning daemon after it finishes its current operation
# Note that this doesnt have to be called when ending the program, as the backend is threadsafe and will close 
# gracefully on its own.
@app.post("/daemon/end")
@require_auth
def end_daemon(auth):

    if daemon_running:
        daemon_running = False
        daemon_sleep.set()
        return create_response("Success", 200)
    
    return create_response("Daemon not running", 500)


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
        
    args = {
        "TCP"                : True,
        "UDP"                : True, 
        "ports"              : [22,80,53,5000],
        "run_ports"          : True,
        "run_os"             : True,
        "run_hostname"       : True,
        "run_mac_vendor"     : True,
        "run_trace"          : True,
        "run_vertical_trace" : True,
    }

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
        run_scan(daemon_network_id, args, token)

        # Waits configurable amount of time before scanning again
        time.sleep(daemon_scan_rate)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Please enter 'remote' or 'local'.")
        sys.exit()

    if sys.argv[1] == "remote":
        # Remote
        DB_SERVER_URL = "http://192.168.12.104:5000"

    elif sys.argv[1] == "local":
        # Local
        DB_SERVER_URL = "http://127.0.0.1:5002"

    else:
        print("Please enter 'remote' or 'local'.")
        sys.exit()

    daemon_thread = threading.Thread(target=run_daemon)
    daemon_thread.daemon = True
    daemon_thread.start()
    app.run(port=5001)