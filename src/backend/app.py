# External
from flask import Flask, request
from flask_cors import CORS 
import jwt
import sys
from functools import wraps
from datetime import timedelta, datetime

# Local
from database import PostgreSQL_database

TOKEN_EXPIRY_MINS = 30

app = Flask(__name__)
CORS(app, allow_headers=["Content-Type", "Auth-Token", "Access-Control-Allow-Credentials"],
     expose_headers="Auth-Token")

app.secret_key = "Security is my passion. This is secure if you think about it i swear."

if len(sys.argv) < 2:
    print("Please enter 'remote' or 'local'.")
    sys.exit()

if sys.argv[1] == "remote":
    # Remote
    DB_SERVER_ADDR = "192.168.12.104"

elif sys.argv[1] == "local":
    # Local
    DB_SERVER_ADDR = "127.0.0.1"

else:
    print("Please enter 'remote' or 'local'.")
    sys.exit()


# Db login info
# TODO add user system, with permissions and logins etc
database = "networks"
user = "postgres"
password = "root"

# Initialises database object
# Temp login information
db = PostgreSQL_database(database, user, password)

# CHECK /documentation/database_API.md FOR RETURN STRUCTURE

# Authentication wrapper
def require_auth(func):

    # Ensures that there is a valid authentication token attached to each request.
    @wraps(func)
    def decorated(*args, **kwargs):
        
        auth = None
        if "Auth-Token" in request.headers:
            auth = request.headers["Auth-Token"]
        else:
            return "Authentication token not in request headers.", 401

        try:
            request_payload = jwt.decode(auth, app.config['SECRET_KEY'], algorithms=["HS256"])
            
            # Checks auth token contents
            if "user_id" not in request_payload.keys():
                return "No user ID contained in authentication token.", 401
            
            if "expiry" not in request_payload.keys():
                return "Malformed auth token.", 401
            
            # Checks if auth token has expired
            if datetime.utcnow() > datetime.strptime(request_payload["expiry"], "%d/%m/%Y/%H/%M/%S"):
                return "Token has expired, login again", 401
            
            # Checks that there is a corresponding user in the database
            user = db.get_user_by_id(request_payload["user_id"])
            if not user:
                return "User doesn't exist.", 401
            
        # If any error occurs, auth token is invalid
        except:
            return "Invalid authentication token.", 401
        
        # Run the decorated function
        return func(user["user_id"], *args, **kwargs)
    
    return decorated


# Adds a user into the database, inputted as json:
# {"username" : , "password" : , "email" : }
@app.post("/signup")
def signup():

    user_data = request.get_json()

    res = db.add_user(user_data)
    if res[1] != 200:
        return res
    
    return "Success.", 200


@app.post("/login")
def login():

    user_data = request.get_json()

    res = db.get_user_by_login(user_data)
    if res[1] != 200:
        return res[0], 401
    
    exp = (datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINS)).strftime("%d/%m/%Y/%H/%M/%S")
    token = jwt.encode({"user_id" : res[0]["user_id"], "expiry" : exp},
                        app.config["SECRET_KEY"], algorithm="HS256")
    
    return token, 200


# Gives basic information about all networks stored in the database, as json:
# [{gateway_mac : , id : , name : , ssid : }, ...]
@app.get("/networks")
@require_auth
def get_networks(user_id):

    return db.get_networks(user_id)


# Gives basic information about the requested network, as json:
# {gateway_mac : , id : , name : , ssid : }
@app.get("/networks/<network_id>")
@require_auth
def get_network(user_id, network_id):

    return db.get_network(user_id, network_id)


# Gives all the devices associated with the given network id, as they were in the most recent scan
@app.get("/networks/<network_id>/devices")
@require_auth
def get_devices(user_id, network_id):
    
    return db.get_all_devices(user_id, network_id)


# Adds a network network to the database, along with its attributes and devices
@app.put("/networks/add")
@require_auth
def save_network(user_id):
    network = request.get_json()
    return db.save_network(user_id, network)


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
@app.post("/networks/<network_id>/rename/<new_name>")
@require_auth
def rename_network(user_id, network_id, new_name):

    return db.rename_network(user_id, network_id, new_name)


# Deletes a network and all related devices from the database
@app.post("/networks/<network_id>/delete")
@require_auth
def delete_network(user_id, network_id):

    return db.delete_network(user_id, network_id)


# Retrieves the logged in user's settings json from the database
@app.get("/settings")
@require_auth
def get_settings(user_id):

    return db.get_settings(user_id)


# Sets a user's settings for scanning and frontend preferences in the database
@app.put("/settings/set")
@require_auth
def set_settings(user_id):

    settings = request.get_json()
    return db.set_settings(user_id, settings)


# Retrieves basic information about all snapshots of a certain network in the databsase
@app.get("/networks/<network_id>/snapshots")
@require_auth
def get_snapshots(user_id, network_id):

    return db.get_snapshots(user_id, network_id)


# Retrieves a specific snapshot of a network at a point in time
@app.get("/networks/<network_id>/snapshots/<timestamp>")
@require_auth
def get_snapshot(user_id, network_id, timestamp):
    
    return db.get_all_devices(user_id, network_id, timestamp)


if __name__ == "__main__":
    app.run(host=DB_SERVER_ADDR, port=5000)