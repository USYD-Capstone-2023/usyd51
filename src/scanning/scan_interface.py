# External
import requests
from flask import Flask
from flask_cors import CORS 
from loading_bar import Loading_bar
from threadpool import Threadpool

# Local
import net_tools as nt

# Stdlib
import json


NUM_THREADS = 50
DB_SERVER_URL = "http://127.0.0.1:5000"

app = Flask(__name__)
CORS(app)

default_settings = {
    "TCP" : True,
    "UDP" : True, 
    "ports": [22,23,80,443],
    "run_ports": False,
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
def scan_network(network_id=-1):

    requests.put(DB_SERVER_URL + "/settings/%d/update" % (0), json=default_settings)
    settings = requests.get(DB_SERVER_URL + "/settings/%d" % (0)).content.decode("utf-8")

    settings = json.loads(settings)

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
    requests.put(DB_SERVER_URL + "/networks/add", json=network.to_json())

    return "success", 200


@app.get("/scan/progress")
def get_progress():

    return lb.get_progress()


# Serves the information of the dhcp server
@app.get("/dhcp")
def get_dhcp_server_info():

    return nt.get_dhcp_server_info(), 200


@app.get("/ssid")
def get_current_ssid():

    return nt.get_ssid(), 200


if __name__ == "__main__":

    app.run(port=5001)