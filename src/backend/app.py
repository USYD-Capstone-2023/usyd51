# External
from flask import Flask, request
import json

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
@app.get("/network/<network_id>")
def get_network(network_id):

    if not db.contains_network(network_id):
        return "Network with ID %d is not present in the database." % (network_id), 500
    
    return db.get_network(network_id)


@app.put("/network/add")
def save_network():

    network = request.get_json()

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


# Serves the information of the dhcp server
@app.get("/network/<network_id>/dhcp")
def get_dhcp_server_info(network_id):

    # TODO
    return db.get_dhcp_info(network_id)


@app.get("/networks")
def get_networks():

    return db.get_networks()


# @app.get("/network/<network_id>/ssid")
# def get_ssid(network_id):

#     return db.get_ssid(network_id)


@app.get("/network/<network_id>/rename/<new_name>")
def rename_network(network_id, new_name):

    if not db.rename_network(network_id, new_name):
        return "Network with id %d not present in database." % (network_id), 500
    
    return "Success", 200


# Deletes a network and all related devices from the database
@app.get("/network/<network_id>/delete")
def delete_network(network_id):

    if not db.delete_network(network_id):
        return "Network with id %d not present in database." % (network_id), 500
    
    return "Success", 200