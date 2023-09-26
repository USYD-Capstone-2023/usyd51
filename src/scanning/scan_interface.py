# External
import requests
from flask import Flask
from flask_cors import CORS 
from loading_bar import Loading_bar
from threadpool import Threadpool

# Local
import net_tools as nt

# Stdlib
import json, sys

NUM_THREADS = 50

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


app = Flask(__name__)
CORS(app)

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

tp = Threadpool(NUM_THREADS)
lb = Loading_bar()

# Finds all devices on the network, runs all scans outlined in users settings
# If a valid network id is entered, it will add the scan results to the database under that ID with a new timestamp,
# otherwise will create a new network in the db
# TODO, this should be POST, currently get to run in browser
@app.get("/scan/<network_id>")
def scan_network(network_id):

    if network_id.isnumeric() or (network_id[0] == '-' and network_id[1:].isnumeric()):
        network_id = int(network_id)
    else:
        return "Invalid network ID", 500 
    
    print(network_id)

    res = requests.put(DB_SERVER_URL + "/settings/%d/set" % (0), json=default_settings)
    if res.status_code != 200:
        return res.content, res.status_code
    
    res = requests.get(DB_SERVER_URL + "/settings/%d" % (0))
    if res.status_code != 200:
            return res.content, res.status_code
    
    settings = json.loads(res.content.decode("utf-8"))

    require = ["run_trace", "run_hostname", "run_vertical_trace", "run_mac_vendor",
               "run_os", "run_ports", "ports"]
    
    args = []
    for req in require:
        if req not in settings.keys():
            print("[ERR ] Malformed settings file, missing required field: %s. Reverting to default settings file." % (req))
            scan_network(network_id)
            return
        
        args.append(settings[req])

    network = nt.scan(lb, tp, network_id, *args)
    res = requests.put(DB_SERVER_URL + "/networks/add", json=network.to_json())
    if res.status_code != 200:
            return res.content, res.status_code

    return "success", 200


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