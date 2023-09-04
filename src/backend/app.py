# External
from flask import Flask

# Local
from loading_bar import Loading_bar
from net_tools import *
from database import PostgreSQLDatabase

# Stdlib
import os

# Ensures that the user has root perms uf run on posix system.
if os.name == "posix" and os.geteuid() != 0: 
    print("Root permissions are required for this program to run.")
    quit()

app = Flask(__name__)

# Initialises database object
# Temp login information
db = PostgreSQLDatabase("net_tool_db", "postgres", "root")

# Initialise loading bar, network utilities and mac vendor lookup table
lb = Loading_bar()
nt = Net_tools(db, lb)


# Gives all the information about the current network that is stored in the database, does not re-run scans
@app.get("/get_devices_no_update")
def current_devices():

    if not db.contains_network(nt.gateway_mac):
        return {"error" : "Current network is not registered in the database, run /map_network to add this network to the database."}
    
    devices = db.get_all_devices(nt.gateway_mac)

    ret = {}
    for device in devices.values():
        ret[device.mac] = device.to_json(); 
    
    return ret


# Finds all devices on the network, traces routes to all of them, resolves mac vendors and hostnames.
# Serves the main mapping data for the program
@app.get("/map_network")
def map_network():

    if not db.contains_network(nt.gateway_mac):
        db.register_network(nt.gateway_mac, nt.domain)

    nt.get_devices()
    nt.add_routes()
    nt.add_mac_vendors()
    # Performs a reverse DNS lookup on all devices in the current network's table of the database 
    nt.add_hostnames()

    return current_devices()

  
# Gets the OS information of the given ip address through TCP fingerprinting
@app.get("/os_info")
def os_scan():

    nt.add_os_info()
    return current_devices()


# Serves the information of the dhcp server
@app.get("/dhcp_info")
def serve_dhcp_server_info():

    return nt.dhcp_server_info


# Returns the progress and data of the current loading bar.
# Polled by frontend to update ui loading bars in electron  
@app.get("/request_progress")
def get_current_progress():

    if lb.total_value == 0:
        return {"flag" : False}

    return {"flag" : True, "progress" : lb.counter, "total" : lb.total_value, "label" : lb.label}


# Deletes a network and all related devices from the database
@app.get("/delete_network/<gateway_id>")
def delete_network(gateway_id):

    db.delete_network(gateway_id)