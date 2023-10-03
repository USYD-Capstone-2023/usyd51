# External
import requests
from flask import Flask, request
from flask_cors import CORS 
from loading_bar import Loading_bar
from threadpool import Threadpool
import threading
from functools import wraps

# Local
import net_tools as nt

# Stdlib
import json, sys

# Total number of threads spawned for the threadpool
NUM_THREADS = 50

app = Flask(__name__)
CORS(app)

tp = Threadpool(NUM_THREADS)
lb = Loading_bar()
daemon_exit = threading.Event()
daemon_exit.set()

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

    # User doesnt exist in settings database, give them default settings
    if res.status_code == 502:
        # Returns user to default settings
        res = requests.put(DB_SERVER_URL + "/settings/set", json=default_settings, headers={"Auth-Token" : auth})
        if res.status_code != 200:
            return None
        
        res = requests.get(DB_SERVER_URL + "/settings", headers={"Auth-Token" : auth})

    if res.status_code != 200:
            return None
    

    # Order of args required to run a scan
    require = ["run_trace", "run_hostname", "run_vertical_trace",
               "run_mac_vendor", "run_os", "run_ports", "ports"]
    
    settings = json.loads(res.content.decode("utf-8"))["content"]

    # Format returned settings data into arguments for scanning function
    args = []
    for req in require:
        if req not in settings.keys():
            return create_response("Settings in database are malformed. Contact your system administrator.", 500)
        
        args.append(settings[req])

    return args


# Checks if a given network ID is valid and numeric
def validate_network_id(network_id):

    if network_id.isnumeric() or network_id == "-1":
        return int(network_id)
    else:
        return None
    

# Runs a network scan on the given network with the given settings arguments.
# Automatically saves network to database on completion.
def run_scan(network_id, args, auth):

    network = nt.scan(lb, tp, network_id, *args)
    res = requests.put(DB_SERVER_URL + "/networks/add", json=network.to_json(), headers={"Auth-Token" : auth})
    if res.status_code != 200:
        return res.content.decode("utf8"), res.status_code

    return res.content.decode("utf8"), res.status_code


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

    network_id = validate_network_id(network_id)

    if network_id == None:
        return create_response("Invalid network ID entered.", 500)
    
    res = verify_current_connection(network_id, auth)
    if res[1] != 200:
        return res[0], res[1]
    
    args = get_settings(auth)

    if args == None:
        return create_response("Malformed settings, automatic reset has failed. Please contact system administrator.", 500)

    return run_scan(network_id, args, auth)
    

# Starts an automatic scanning daemon on the network specified.
# Scans are conducted at the interval specified in the user's settings table (NOT IMPLEMENTED, HARDCODED ABOVE CURRENTLY)
# The daemon will be shutdown after the end_daemon method is called, or if it encounters a specific number of 
# consecutive database faults.
@app.post("/daemon/start/<network_id>")
@require_auth
def start_daemon(auth, network_id):

    # Ensures only one daemon is running at a time (Although the backend is built to handle multiple, just need to add
    # unique IDs for each process if we want this to be a feature).
    if not daemon_exit.is_set():
        print("[ERR ] Scan daemon is already running.")
        return create_response("Daemon already running", 500)

    # Checks network ID is valid
    network_id = validate_network_id(network_id)
    if network_id == None or network_id < 0:
        return create_response("Invalid network ID entered.", 500)
    
    # Checks that the server is currently connected to the requested network
    res = verify_current_connection(network_id, auth)
    if res[1] != 200:
        return res
    
    # Retrieves user's settings from the database
    args = get_settings(auth)
    if args == None:
        return create_response("Malformed settings, automatic reset has failed. Please contact system administrator.", 500)
    
    # Hardcoded fault limit, will be moved to user settings 
    consecutive_fault_limit = 3
    consecutive_faults = 0
    daemon_exit.clear()

    print("[INFO] Daemon is starting!")
    while not daemon_exit.is_set():

        # If the scans fail to be written to the database a certain number of times, the daemon exits
        if consecutive_faults == consecutive_fault_limit:
            daemon_exit.set()
            print("[INFO] Scan daemon closing due to consecutive errors.")
            return create_response("Reached maximum number of consecutive failures. Daemon mode terminated.", 500)

        if run_scan(network_id, args, auth)[1] != 200:
            print("[ERR ] Failed to write scanned data to remote database. %d attempts remaining..." % \
                  (consecutive_fault_limit - consecutive_faults))
            
            consecutive_faults += 1

        elif consecutive_faults != 0:
            consecutive_faults = 0

        # Waits configurable amount of time before scanning again
        daemon_exit.wait(daemon_scan_rate)

    return create_response("Success", 200)


# Sets the flag to kill the scanning daemon after it finishes its current operation
# Note that this doesnt have to be called when ending the program, as the backend is threadsafe and will close 
# gracefully on its own.
@app.post("/daemon/end")
def end_daemon():

    print("[INFO] Scan daemon will shut down after current operation.")
    daemon_exit.set()

    return create_response("Success", 200)


@app.get("/scan/progress")
def get_progress():

    return create_response("success", 200, content=lb.get_progress())


# Serves the information of the dhcp server
@app.get("/dhcp")
def get_dhcp_server_info():

    return create_response("success", 200, content=nt.get_dhcp_server_info())


@app.get("/ssid")
def get_current_ssid():

    return create_response("success", 200, nt.get_ssid())


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

    app.run(port=5001)