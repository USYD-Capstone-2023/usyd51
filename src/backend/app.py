# External
from flask import Flask, request, jsonify

# Local
from database import PostgreSQL_database

app = Flask(__name__)

# Db login info
# TODO add user system, with permissions and logins etc
database = "networks"
user = "postgres"
password = "root"

# Initialises database object
# Temp login information
db = PostgreSQL_database(database, user, password)

# Gives all the information about the current network that is stored in the database, does not re-run scans
@app.get("/networks/<network_id>")
def get_network(network_id):

    if not db.contains_network(network_id):
        return "Network with ID %d is not present in the database." % (network_id), 500
    
    return db.get_network(network_id)


# Gives all the devices associated with the given network id, as they were in the most recent scan
@app.get("/networks/<network_id>/devices")
def get_devices(network_id):

    if not db.contains_network(network_id):
        return "Network with ID %d is not present in the database." % (network_id), 500
    
    return db.get_all_devices(network_id)


# Adds a network network to the database, along with its attributes and devices
@app.put("/networks/add")
def save_network():

    network = request.get_json()

    # Ensures given data is correctly formed
    required = ["network_id", "devices", "timestamp"]
    for req in required:
        if req not in network.keys():
            return "Malformed network.", 500
            
    id = network["network_id"]
    devices = network["devices"]
    ts = network["timestamp"]

    # Registers a new network with ssid as its name if the given id doesnt exist or is invalid
    if id == -1 or not db.contains_network(id):
        id = db.get_next_network_id()
        network["network_id"] = id
        if not db.register_network(network):
            return "Database encountered an error registering new network", 500
    
    if db.save_devices(id, devices, ts):
        return "Success", 200
    return "Database encountered an error saving devices", 500


# Updates an the most recent scan data of existing network in the database, 
# without creating a new snapshot in its history
@app.put("/networks/<network_id>/update")
def update_devices(network_id):

    if not db.contains_network(id):
        return "No network with ID %d exists in database." % (network_id), 500
    
    network = request.get_json()

    # Ensures given data is correctly formed
    required = ["network_id", "devices"]
    for req in required:
        if req not in network.keys():
            return "Malformed network.", 500
            
    id = network["network_id"]
    devices = network["devices"]
    
    for device in devices:
        if not db.update_device(network_id, device):
            return "Database encountered an error saving devices", 500
    return "Success", 200


@app.get("/networks")
def get_networks():

    return db.get_networks()


# TODO - These ones are gets just for testing purposes at the minute, so I can test them
# in browser while the frontend isnt hooked up
@app.get("/networks/<network_id>/rename/<new_name>")
def rename_network(network_id, new_name):

    if not db.rename_network(network_id, new_name):
        return "Network with id %d not present in database." % (network_id), 500
    
    return "Success", 200


# Deletes a network and all related devices from the database
@app.get("/networks/<network_id>/delete")
def delete_network(network_id):

    if not db.delete_network(network_id):
        return "Network with id %d not present in database." % (network_id), 500
    
    return "Success", 200


# Retrieves a users settings json from the database
@app.get("/settings/<user_id>")
def get_settings(user_id):

    settings = db.get_settings(user_id)
    return settings


# Sets a users settings in the database
@app.put("/settings/<user_id>/update")
def set_settings(user_id):

    settings = request.get_json()
    require = ["TCP", "UDP", "ports", "run_ports", "run_os", "run_hostname", 
               "run_mac_vendor", "run_trace", "run_vertical_trace", "defaultView",
               "defaultNodeColour", "defaultEdgeColour", "defaultBackgroundColour"]

    for req in require:
        if req not in settings.keys():
            print("err")
            return "Malformed settings file.", 500

    if db.update_settings(user_id, settings):
        return "Database error.", 500

    return "Success", 200