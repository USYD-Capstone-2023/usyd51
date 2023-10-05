# External
from flask import Flask, request
from flask_cors import CORS
import jwt
import sys
from functools import wraps
from datetime import timedelta, datetime

# Local
from config import Config
from database import PostgreSQL_database as pdb

TOKEN_EXPIRY_MINS = 30

app = None
db = None

app = Flask(__name__)

# Load the configuration from the specified config class
app.config.from_object(Config)

# When run by name, define the app configuration based on command line args
if len(sys.argv) < 2:
    print("Please enter either 'remote' or 'local'")
    sys.exit(-1)

if sys.argv[1] == "remote":
    app.config.from_object("config.RemoteConfig")

elif sys.argv[1] == "local":
    app.config.from_object("config.LocalConfig")

elif sys.argv[1] == "testing":
    app.config.from_object("config.TestingConfig")

else:
    print("Please enter either 'remote' or 'local'")
    sys.exit(-1)

CORS(app, allow_headers=["Content-Type", "Auth-Token", "Access-Control-Allow-Credentials"],
    expose_headers="Auth-Token")

db = pdb(app.config["DATABASE_NAME"], "postgres", "root")

# CHECK /documentation/database_API.md FOR RETURN STRUCTURE

def create_response(message, code, content=""):

    return {"message" : message, "status" : code, "content" : content}, code


# Authentication wrapper
def require_auth(func):

    # Ensures that there is a valid authentication token attached to each request.
    @wraps(func)
    def decorated(*args, **kwargs):
        
        auth = None
        if "Auth-Token" in request.headers:
            auth = request.headers["Auth-Token"]
        else:
            return create_response("Authentication token not in request headers.", 401)
        

        try:
            request_payload = jwt.decode(auth, app.config['SECRET_KEY'], algorithms=["HS256"])
            
            # Checks auth token contents
            if "user_id" not in request_payload.keys():
                return create_response("No user ID contained in authentication token.", 401)
            
            if "expiry" not in request_payload.keys():
                return create_response("Malformed auth token.", 401)
            
            # Checks if auth token has expired
            if datetime.utcnow() > datetime.strptime(request_payload["expiry"], "%d/%m/%Y/%H/%M/%S"):
                return create_response("Token has expired, login again", 401)
            
            # Checks that there is a corresponding user in the database
            res = db.get_user_by_id(request_payload["user_id"])
            if res[1] != 200:
                return create_response(*res)
            
        # If any error occurs, auth token is invalid
        except Exception as e:
            return create_response("Invalid authentication token.", 401)
        
        # Run the decorated function
        return func(res[2]["user_id"], *args, **kwargs)
    return decorated


def to_ints(vals):
    for i in range(len(vals)):
        try:
            vals[i] = int(vals[i])
        except:
            return None
        
    return vals
            

# Adds a user into the database, inputted as json:
# {"username" : , "password" : , "email" : }
@app.post("/signup")
def signup():
    user_data = request.get_json()
    res = db.add_user(user_data)
    if res[1] != 200:
        return res
    
    return create_response("Success.", 200)


# Logs in a user, returns an authentication token to authenticate further access:
# {"username" : , "password" : }
@app.post("/login")
def login():
    user_data = request.get_json()
    res = db.get_user_by_login(user_data)
    if res[1] != 200:
        return create_response(res[0], 401)
    
    exp = (datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINS)).strftime("%d/%m/%Y/%H/%M/%S")
    token = jwt.encode({"user_id" : res[2]["user_id"], "expiry" : exp},
                        app.config["SECRET_KEY"], algorithm="HS256")
    
    return create_response("Success.", 200, {"Auth-Token" : token})


# Gives basic information about all networks stored in the database, as json:
# [{gateway_mac : , id : , name : , ssid : }, ...]
@app.get("/networks")
@require_auth
def get_networks(user_id):
    ret = db.get_networks(user_id)
    return create_response(*ret) 


# Gives basic information about the requested network, as json:
# {gateway_mac : , id : , name : , ssid : }
@app.get("/networks/<network_id>")
@require_auth
def get_network(user_id, network_id):
    args = to_ints([network_id])
    if not args:
        return create_response(pdb.err_codes["bad_input"][0], pdb.err_codes["bad_input"][1])

    ret = db.get_network(user_id, args[0])
    return create_response(*ret) 


# Gives all the devices associated with the given network id, as they were in the most recent scan
@app.get("/networks/<network_id>/devices")
@require_auth
def get_devices(user_id, network_id):
    args = to_ints([network_id])
    if not args:
        return create_response(pdb.err_codes["bad_input"][0], pdb.err_codes["bad_input"][1])

    ret = db.get_all_devices(user_id, args[0])
    return create_response(*ret) 


# Adds a network network to the database, along with its attributes and devices
@app.put("/networks/add")
@require_auth
def save_network(user_id):
    network = request.get_json()
    ret = db.save_network(user_id, network)
    return create_response(*ret)


@app.put("/networks/<network_id>/update")
@require_auth
def update_network(user_id, network_id):

    args = to_ints([network_id])
    if not args:
        return create_response(pdb.err_codes["bad_input"][0], pdb.err_codes["bad_input"][1])

    network = request.get_json()
    ret = db.save_network(user_id, network_id, network, exists=True)
    return create_response(*ret)


# Renames a network in the database
@app.put("/networks/<network_id>/rename/<new_name>")
@require_auth
def rename_network(user_id, network_id, new_name):
    args = to_ints([network_id])
    if not args:
        return create_response(pdb.err_codes["bad_input"][0], pdb.err_codes["bad_input"][1])
    
    ret = db.rename_network(user_id, args[0], new_name)
    return create_response(*ret)


# Deletes a network and all related devices from the database
@app.post("/networks/<network_id>/delete")
@require_auth
def delete_network(user_id, network_id):
    args = to_ints([network_id])
    if not args:
        return create_response(pdb.err_codes["bad_input"][0], pdb.err_codes["bad_input"][1])
    
    ret = db.delete_network(user_id, args[0])
    return create_response(*ret) 


# Retrieves the logged in user's settings json from the database
@app.get("/settings")
@require_auth
def get_settings(user_id):

    ret = db.get_settings(user_id)
    return create_response(*ret) 


# Sets a user's settings for scanning and frontend preferences in the database
@app.put("/settings/set")
@require_auth
def set_settings(user_id):

    settings = request.get_json()
    ret = db.set_settings(user_id, settings)
    return create_response(*ret) 


# Retrieves basic information about all snapshots of a certain network in the databsase
@app.get("/networks/<network_id>/snapshots")
@require_auth
def get_snapshots(user_id, network_id):
    args = to_ints([network_id])
    if not args:
        return create_response(pdb.err_codes["bad_input"][0], pdb.err_codes["bad_input"][1])
    
    ret = db.get_snapshots(user_id, args[0])
    return create_response(*ret) 


# Retrieves a specific snapshot of a network at a point in time
@app.get("/networks/<network_id>/snapshots/<timestamp>")
@require_auth
def get_snapshot(user_id, network_id, timestamp):
    args = to_ints([network_id, timestamp])
    if not args:
        return create_response(pdb.err_codes["bad_input"][0], pdb.err_codes["bad_input"][1])

    ret = db.get_all_devices(user_id, args[0], args[1])
    return create_response(*ret) 


if __name__=="__main__":
    app.run(host=app.config["SERVER_URI"], port=app.config["SERVER_PORT"])