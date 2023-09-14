# External
from flask import Flask

# Local
from loading_bar import Loading_bar
from net_tools import *
from database import SQLiteDB

# Stdlib
import os

# Ensures that the user has root perms uf run on posix system.
if os.name == "posix" and os.geteuid() != 0: 
    print("Root permissions are required for this program to run.")
    quit()

app = Flask(__name__)

# Initialises database object
# Temp login information
db = SQLiteDB("networks.db")

# Initialise loading bar, network utilities and mac vendor lookup table
lb = Loading_bar()
nt = Net_tools(db, lb)


# Gives all the information about the current network that is stored in the database, does not re-run scans
@app.get("/network/<network_id>")
def get_network(network_id):

    if not db.contains_network(network_id):
        return {"error" : "Current network is not registered in the database, run /map_network to add this network to the database."}
    
    devices = db.get_all_devices(network_id)

    ret = {}
    for device in devices.values():
        ret[device.mac] = device.to_json()
    return ret


# Finds all devices on the network, traces routes to all of them, resolves mac vendors and hostnames.
# Serves the main mapping data for the program
@app.get("/map_network")
def map_network():

    # Creates a new network in the backend, begins passive scanning and adds to database
    if not nt.new_network():
        return {"error" : "Failed to scan network, are you connected to the internet?"}

    # Adds all active devices on the network to the database
    nt.get_devices()
    # Runs a vertical traceroute to the last internal network device
    nt.vertical_traceroute()
    # Adds routing information for all devicesin the database
    nt.add_routes()
    # Looks up mac vendor for all devices in the database
    nt.add_mac_vendors()
    # Performs a reverse DNS lookup on all devices in the current network's table of the database 
    nt.add_hostnames()

    devices = db.get_all_devices(nt.network_id)
    ret = {}
    for device in devices.values():
        ret[device.mac] = device.to_json()
    return ret

  
# Gets the OS information of the given ip address through TCP fingerprinting
@app.get("/os_info")
def os_scan():

    nt.add_os_info()
    return get_network(nt.network_id)


# Serves the information of the dhcp server
@app.get("/dhcp_info")
def get_dhcp_server_info():

    return nt.dhcp_server_info


@app.get("/network_names")
def get_network_names():

    return db.get_network_names()


@app.get("/ssid")
def get_ssid():

    ret = nt.get_ssid()
    return "error" if ret == None else ret


@app.get("/id")
def get_id():

    return error if nt.network_id == None else nt.network_id


@app.get("/ports/<network_id>")
def get_ports(network_id):

    nt.add_ports(network_id)

    devices = db.get_all_devices(network_id)

    ret = {}
    for device in devices.values():
        ret[device.mac] = device.to_json()
    return ret


@app.get("/rename_network/<network_id>,<new_name>")
def rename_network(network_id, new_name):

    if db.rename_network(network_id, new_name):
        return "success"
    
    return "error"


# Returns the progress and data of the current loading bar.
# Polled by frontend to update ui loading bars in electron  
@app.get("/request_progress")
def get_current_progress():

    if lb.total_value == 0:
        return {"flag" : False}

    return {"flag" : True, "progress" : lb.counter, "total" : lb.total_value, "label" : lb.label}


# Deletes a network and all related devices from the database
@app.get("/delete_network/<network_id>")
def delete_network(network_id):

    if db.delete_network(network_id):
        return "Successfully deleted network"

    return "Could not find entered network..."
