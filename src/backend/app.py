# External
from flask import Flask, request
from flask_cors import CORS 

# Local
from database import PostgreSQL_database

app = Flask(__name__)
CORS(app)

# stub data for settings prototyping
settings_json = {"user_id" : 0,
               "TCP" : False,
               "UDP" : False,
               "ports" : [],
               "run_ports" : False,
               "run_os" : False,
               "run_hostname" : False,
               "run_mac_vendor" : False,
               "run_trace" : False,
               "run_vertical_trace" : False,
               "defaultView" : "Hierarchical",
               "defaultNodeColour" : "aaffff",
               "defaultEdgeColour" : "ffaaff",
               "defaultBackgroundColour" : "ffffaa"}

# Db login info
# TODO add user system, with permissions and logins etc
database = "networks"
user = "postgres"
password = "root"

# Initialises database object
# Temp login information
db = PostgreSQL_database(database, user, password)

# CHECK /documentation/database_API.md FOR RETURN STRUCTURE

# Gives basic information about all networks stored in the database, as json:
# [{gateway_mac, id, name, ssid}, ...]
@app.get("/networks")
def get_networks():

    return db.get_networks()


# Gives basic information about the requested network, as json:
# {gateway_mac, id, name, ssid}
@app.get("/networks/<network_id>")
def get_network(network_id):

    return db.get_network(network_id)


# Gives all the devices associated with the given network id, as they were in the most recent scan
@app.get("/networks/<network_id>/devices")
def get_devices(network_id):
    
    return db.get_all_devices(network_id)


# Adds a network network to the database, along with its attributes and devices
@app.put("/networks/add")
def save_network():
    network = request.get_json()
    return db.save_network(network)

# Stub for getting settings data
@app.get("/getsettings/<user_id>")
def get_setting(user_id):
    return settings_json

# Stub for setting settings data
@app.put("/setsettings/<user_id>/set")
def set_setting(user_id):
    settings = request.get_json()

    for setting, status in settings.items():
        if setting in set(("UDP", "TCP", "run_ports", "run_os", "run_hostname", "run_mac_vendor", "run_trace", "run_vertical_trace")):
            if status in [True, False]:
                settings_json[setting] = status

    return ("Success.", 200)


# Updates the most recent scan data of an existing network in the database, 
# without creating a new snapshot in its history

# NOT IMPLEMENTED CURRENTLY, WANT TO CLARIFY OPERATION FIRST 

# @app.put("/networks/<network_id>/update")
# def update_devices(network_id):

#     if not db.contains_network(id):
#         return "No network with ID %s exists in database." % (network_id), 500
    
#     network = request.get_json()

#     # Ensures given data is correctly formed
#     required = ["network_id", "devices"]
#     for req in required:
#         if req not in network.keys():
#             return "Malformed network.", 500
            
#     id = network["network_id"]
#     devices = network["devices"]
    
#     for device in devices:
#         if not db.update_device(network_id, device):
#             return "Database encountered an error saving devices", 500

#     return "Success", 200


# TODO - These ones are GETS just for testing purposes at the minute, so I can test them
# in browser while the frontend isnt hooked up, will be POST
@app.get("/networks/<network_id>/rename/<new_name>")
def rename_network(network_id, new_name):

    return db.rename_network(network_id, new_name)


# Deletes a network and all related devices from the database
@app.get("/networks/<network_id>/delete")
def delete_network(network_id):

    return db.delete_network(network_id)


# Retrieves a users settings json from the database
@app.get("/settings/<user_id>")
def get_settings(user_id):

    return db.get_settings(user_id)


# Sets a user's settings for scanning and frontend preferences in the database
@app.put("/settings/<user_id>/set")
def set_settings(user_id):

    settings = request.get_json()
    return db.set_settings(user_id, settings)


# Retrieves basic information about all snapshots of a certain network in the databsase
@app.get("/networks/<network_id>/snapshots")
def get_snapshots(network_id):

    return db.get_snapshots(network_id)


# Retrieves a specific snapshot of a network at a point in time
@app.get("/networks/<network_id>/snapshots/<timestamp>")
def get_snapshot(network_id, timestamp):
    
    return db.get_all_devices(network_id, timestamp)