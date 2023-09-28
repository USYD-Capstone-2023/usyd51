# External
import requests
from flask import Flask
from flask_cors import CORS 
from loading_bar import Loading_bar
from threadpool import Threadpool
import threading

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


if len(sys.argv) < 2:
    print("Please enter 'remote' or 'local'.")
    sys.exit()

if sys.argv[1] == "remote":
    # Remote
    DB_SERVER_URL = "http://192.168.12.104:5000"

elif sys.argv[1] == "local":
    # Local
    DB_SERVER_URL = "http://127.0.0.1:5000"

else:
    print("Please enter 'remote' or 'local'.")
    sys.exit()


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


# Retrieves a given user's settings from the database, adds them if they are non existent
def get_settings(user_id):

    res = requests.get(DB_SERVER_URL + "/settings/%d" % (0))

    # User doesnt exist in settings database, give them default settings
    if res.status_code == 502:
        # Returns user to default settings
        res = requests.put(DB_SERVER_URL + "/settings/%d/set" % (0), json=default_settings)
        if res.status_code != 200:
            return None
        
        res = requests.get(DB_SERVER_URL + "/settings/%d" % (0))

    if res.status_code != 200:
            return None
    

    require = ["run_trace", "run_hostname", "run_vertical_trace",
               "run_mac_vendor", "run_os", "run_ports", "ports"]
    
    settings = json.loads(res.content.decode("utf-8"))

    args = []
    for req in require:
        if req not in settings.keys():
            return "Settings in database are malformed. Contact your system administrator.", 500
        
        args.append(settings[req])

    return args


# Checks if a given network ID is valid and numeric
def validate_network_id(network_id):

    if network_id.isnumeric() or (network_id[0] == '-' and network_id[1:].isnumeric()):
        return int(network_id)
    else:
        return None
    

# Runs a network scan on the given network with the given settings arguments.
# Automatically saves network to database on completion.
def run_scan(network_id, args):

    network = nt.scan(lb, tp, network_id, *args)
    res = requests.put(DB_SERVER_URL + "/networks/add", json=network.to_json())
    if res.status_code != 200:
            return res.content, res.status_code

    return "success", 200


def verify_current_connection(network_id):

    network = requests.get(DB_SERVER_URL + "/networks/%s" % (network_id))
    
    # Network hasnt been created, so should be valid to run a scan
    if network.status_code == 500:
        return True
    
    # An error occurred
    if network.status_code != 200:
        return False

    network = json.loads(network.content.decode("utf-8"))

    # Check that the network being scanned corresponds to the one in the database
    gateway_mac = nt.get_gateway_mac()
    if "gateway_mac" not in network.keys() or network["gateway_mac"] != gateway_mac:
        return False
    
    return True


# Finds all devices on the network, runs all scans outlined in users settings
# If a valid network id is entered, it will add the scan results to the database under that ID with a new timestamp,
# otherwise will create a new network in the db
# TODO, this should be POST, currently get to run in browser
@app.get("/scan/<network_id>")
def scan_network(network_id):

    network_id = validate_network_id(network_id)

    if network_id == None:
        return "Invalid network ID entered.", 500
    
    if not verify_current_connection(network_id):
        return "Not currently connected to network.", 500
    
    args = get_settings(0)

    if args == None:
        return "Malformed settings, automatic reset has failed. Please contact system administrator.", 500

    return run_scan(network_id, args)
    

# Starts an automatic scanning daemon on the network specified.
# Scans are conducted at the interval specified in the user's settings table (NOT IMPLEMENTED, HARDCODED ABOVE CURRENTLY)
# The daemon will be shutdown after the end_daemon method is called, or if it encounters a specific number of 
# consecutive database faults.
@app.get("/daemon/start/<network_id>")
def start_daemon(network_id):

    # Ensures only one daemon is running at a time (Although the backend is built to handle multiple, just need to add
    # unique IDs for each process if we want this to be a feature).
    if not daemon_exit.is_set():
        print("[ERR ] Scan daemon is already running.")
        return "Daemon already running", 500

    # Checks network ID is valid
    network_id = validate_network_id(network_id)
    if network_id == None or network_id < 0:
        return "Invalid network ID entered.", 500
    
    # Retrieves user's settings from the database
    args = get_settings(0)
    if args == None:
        return "Malformed settings, automatic reset has failed. Please contact system administrator.", 500
    
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
            return "Reached maximum number of consecutive failures. Daemon mode terminated.", 500

        if run_scan(network_id, args)[1] != 200:
            print("[ERR ] Failed to write scanned data to remote database. %d attempts remaining..." % \
                  (consecutive_fault_limit - consecutive_faults))
            
            consecutive_faults += 1

        elif consecutive_faults != 0:
            consecutive_faults = 0

        # Waits configurable amount of time before scanning again
        daemon_exit.wait(daemon_scan_rate)

    return "Success", 200


# Sets the flag to kill the scanning daemon after it finishes its current operation
# Note that this doesnt have to be called when ending the program, as the backend is threadsafe and will close 
# gracefully on its own.
@app.get("/daemon/end")
def end_daemon():

    print("[INFO] Scan daemon will shut down after current operation.")
    daemon_exit.set()

    return "Success", 200


@app.get("/scan/progress")
def get_progress():

    return lb.get_progress(), 200


# Serves the information of the dhcp server
@app.get("/dhcp")
def get_dhcp_server_info():

    return nt.get_dhcp_server_info(), 200


@app.get("/ssid")
def get_current_ssid():

    return nt.get_ssid(), 200


if __name__ == "__main__":

    app.run(port=5001)