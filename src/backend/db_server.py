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
from response import Response

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


# Authentication wrapper
def require_auth(func):

    # Ensures that there is a valid authentication token attached to each request.
    @wraps(func)
    def decorated(*args, **kwargs):
        
        auth = None
        if "Auth-Token" in request.headers:
            auth = request.headers["Auth-Token"]
        else:
            return Response("Authentication token not in request headers.", 401)

        try:
            request_payload = jwt.decode(auth, app.config['SECRET_KEY'], algorithms=["HS256"])
            
            # Checks auth token contents
            if "user_id" not in request_payload.keys():
                return Response("no_auth")
            
            if "expiry" not in request_payload.keys():
                return Response("malformed_auth")
            
            # Checks if auth token has expired
            if datetime.utcnow() > datetime.strptime(request_payload["expiry"], "%d/%m/%Y/%H/%M/%S"):
                return Response("expired_auth")
            
            # Checks that there is a corresponding user in the database
            res = db.get_user_by_id(request_payload["user_id"])
            if res.status != 200:
                return res.to_json()
            
        # If any error occurs, auth token is invalid
        except Exception as e:
            return Response("malformed_auth")
        
        # Run the decorated function
        return func(res.content["user_id"], *args, **kwargs)
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
    if res.status != 200:
        return res
    
    return Response("success").json()


# Logs in a user, returns an authentication token to authenticate further access:
# {"username" : , "password" : }
@app.post("/login")
def login():

    user_data = request.get_json()

    if "username" not in user_data.keys() or "password" not in user_data.keys():
        return Response("malformed_user").to_json()

    res = db.get_user_by_login(user_data["username"], user_data["password"])
    if res.status != 200:
        return res.to_json()
    
    exp = (datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINS)).strftime("%d/%m/%Y/%H/%M/%S")
    token = jwt.encode({"user_id" : res.content["user_id"], "expiry" : exp},
                        app.config["SECRET_KEY"], algorithm="HS256")
    
    return Response("success", content={"Auth-Token" : token}).to_json()


# Gives basic information about all networks stored in the database, as json:
# [{gateway_mac : , id : , name : , ssid : }, ...]
@app.get("/networks")
@require_auth
def get_networks(user_id):

    return db.get_networks(user_id).to_json()
    

# Gives basic information about the requested network, as json:
# {gateway_mac : , id : , name : , ssid : }
@app.get("/networks/<network_id>")
@require_auth
def get_network(user_id, network_id):

    args = to_ints([network_id])
    if not args:
        return Response("bad_input").to_json()

    return db.get_network(user_id, args[0]).to_json()
    

# Gives all the devices associated with the given network id, as they were in the most recent scan
@app.get("/networks/<network_id>/devices")
@require_auth
def get_devices(user_id, network_id):

    args = to_ints([network_id])
    if not args:
        return Response("bad_input").to_json()

    return db.get_all_devices(user_id, args[0]).to_json()
     

# Adds a network network to the database, along with its attributes and devices
@app.put("/networks/add")
@require_auth
def save_network(user_id):

    network = request.get_json()
    return db.save_network(user_id, network).to_json()
    

# Updates an existing snapshot of a network in place
@app.put("/networks/update")
@require_auth
def update_network(user_id):

    network = request.get_json()
    return db.save_network(user_id, network, exists=True).to_json()
    

# Renames a network in the database
@app.put("/networks/<network_id>/rename/<new_name>")
@require_auth
def rename_network(user_id, network_id, new_name):

    args = to_ints([network_id])
    if not args:
        return Response("bad_input").to_json()
    
    return db.rename_network(user_id, new_name).to_json()


# Deletes a network and all related devices from the database
@app.post("/networks/<network_id>/delete")
@require_auth
def delete_network(user_id, network_id):

    args = to_ints([network_id])
    if not args:
        return Response("bad_input").to_json()
    
    return db.delete_network(user_id, args[0]).to_json()


# Retrieves the logged in user's settings json from the database
@app.get("/settings")
@require_auth
def get_settings(user_id):

    return db.get_settings(user_id).to_json()


# Sets a user's settings for scanning and frontend preferences in the database
@app.put("/settings/set")
@require_auth
def set_settings(user_id):

    settings = request.get_json()
    return db.set_settings(user_id, settings).to_json() 


# Retrieves basic information about all snapshots of a certain network in the databsase
@app.get("/networks/<network_id>/snapshots")
@require_auth
def get_snapshots(user_id, network_id):
    args = to_ints([network_id])
    if not args:
        return Response("bad_input").to_json()
    
    return db.get_snapshots(user_id, args[0]).to_json()


# Retrieves a specific snapshot of a network at a point in time
@app.get("/networks/<network_id>/snapshots/<timestamp>")
@require_auth
def get_snapshot(user_id, network_id, timestamp):
    args = to_ints([network_id, timestamp])
    if not args:
        return Response("bad_input").to_json()

    return db.get_all_devices(user_id, args[0], args[1]).to_json() 


if __name__=="__main__":
    app.run(host=app.config["SERVER_URI"], port=app.config["SERVER_PORT"])
