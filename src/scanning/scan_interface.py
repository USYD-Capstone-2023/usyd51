import  sys

# External
import requests
from flask import Flask
from loading_bar import Loading_bar

app = Flask(__name__)

# Local
import net_tools as nt

# Stdlib
import os, json

DB_SERVER_URL = "http://127.0.0.1:5000"


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



# Finds all devices on the network, runs all scans outlined in users settings
# If a valid network id is entered, it will add the scan results to the database under that ID with a new timestamp,
# otherwise will create a new network in the db

# TODO, this should be PUT, currently get to run in browser
@app.get("/scan")
def scan_network(network_id=-1):

    lb = Loading_bar()

    res = requests.put(DB_SERVER_URL + "/settings/%d/set" % (0), json=default_settings)
    settings = requests.get(DB_SERVER_URL + "/settings/%d" % (0)).content.decode("utf-8")

    settings = json.loads(settings)

    require = ["run_trace", "run_hostname", "run_vertical_trace", "run_mac_vendor",
               "run_os", "run_ports", "ports"]
    
    args = []
    for req in require:
        if req not in settings.keys():
            print("[ERR ] Malformed settings file, missing required field: %s. Reverting to default settings file." % (req))
            set_default_settings()
            scan_network(network_id)
            return
        
        args.append(settings[req])

    nt.scan(lb, network_id, *args)


@app.get("/scan/progress")
def get_progress():

    return -1


# Serves the information of the dhcp server
@app.get("/dhcp")
def get_dhcp_server_info():

    return nt.get_dhcp_server_info(), 200


@app.get("/ssid")
def get_current_ssid():

    return nt.get_ssid(), 200


if __name__ == "__main__":

    app.run(port=5001)