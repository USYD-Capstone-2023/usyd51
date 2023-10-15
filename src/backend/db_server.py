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

TOKEN_EXPIRY_MINS = 525600

app = None
db = None

app = Flask(__name__)

# Load the configuration from the specified config class
app.config.from_object(Config)

# Define the app configuration based on command line args
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

# Return formatting wrapper
def returns_response_obj(func):

    # Converts the Resonse return into a valid flask HTTP response
    @wraps(func)
    def res_decorator(*args, **kwargs):
        
        # Run the decorated function
        res = func(*args, **kwargs)

        if isinstance(res, Response):
            content, status = res.to_json()
            return content, status
        
        content, status = Response("db_error").to_json()
        return content, status, {"Access-Control-Allow-Origin": "*"}
        
    return res_decorator


# Authentication wrapper
def require_auth(func):

    # Ensures that there is a valid authentication token attached to each request.
    @wraps(func)
    def auth_decorator(*args, **kwargs):
        
        auth = None
        if "Auth-Token" in request.headers:
            auth = request.headers["Auth-Token"]
        else:
            return Response("no_auth", 401)

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
                return res
            
            # Converts user id to integer
            res.content["user_id"] = int(res.content["user_id"])
            
        # If any error occurs, auth token is invalid
        except Exception as e:
            return Response("malformed_auth")
            
        # Run the decorated function
        return func(res.content["user_id"], *args, **kwargs)
    return auth_decorator


# Checks if input values are numerical and converts to integers or None if not
def to_ints(vals):

    for i in range(len(vals)):
        try:
            vals[i] = int(vals[i])
        except:
            return None
        
    return vals
            

# Adds a user into the database when they signup to the app
@app.post("/signup")
@returns_response_obj
def signup():

    user_data = None   
    try:
        user_data = request.get_json()
    except:
        return Response("bad_input")
        
    res = db.add_user(user_data)
    if res.status != 200:
        return res
    
    return Response("success")
    

# Logs in a user, returns an authentication token to authenticate further access:
@app.post("/login")
@returns_response_obj
def login():

    user_data = None   
    try:
        user_data = request.get_json()
    except:
        return Response("bad_input")
        
    if "username" not in user_data.keys() or "password" not in user_data.keys():
        return Response("malformed_user")
    
    res = db.get_user_by_login(user_data["username"], user_data["password"])
    if res.status != 200:
        return res
        
    exp = (datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINS)).strftime("%d/%m/%Y/%H/%M/%S")
    token = jwt.encode({"user_id" : res.content["user_id"], "expiry" : exp},
                        app.config["SECRET_KEY"], algorithm="HS256")
    
    return Response("success", content={"Auth-Token" : token})
    

# Gives basic information about all networks accessible by the user.
@app.get("/networks")
@returns_response_obj
@require_auth
def get_networks(user_id):

    return db.get_networks(user_id)
    

# Gives basic information about the requested network.
@app.get("/networks/<network_id>")
@returns_response_obj
@require_auth
def get_network(user_id, network_id):

    args = to_ints([network_id])
    if not args:
        return Response("bad_input")

    return db.get_network(user_id, args[0])
    

# Gives all the devices associated with the given network id, as they were in the most recent scan
@app.get("/networks/<network_id>/devices")
@returns_response_obj
@require_auth
def get_devices(user_id, network_id):

    args = to_ints([network_id])
    if not args:
        return Response("bad_input")
        
    return db.get_all_devices(user_id, args[0])
     

# Adds a network network to the database, along with its attributes and devices
@app.put("/networks/add")
@returns_response_obj
@require_auth
def save_network(user_id):

    network = None
    try:
        network = request.get_json()
    except:
        return Response("bad_input")
        
    network["user_id"] = user_id
    return db.save_network(user_id, network)
    

# Updates an existing snapshot of a network in place
@app.put("/networks/update")
@returns_response_obj
@require_auth
def update_network(user_id):

    network = None
    try:
        network = request.get_json()
    except:
        return Response("bad_input")
        
    network["user_id"] = user_id
    return db.save_network(user_id, network, exists=True)
    

# Renames a network in the database
@app.put("/networks/<network_id>/rename/<new_name>")
@returns_response_obj
@require_auth
def rename_network(user_id, network_id, new_name):

    args = to_ints([network_id])
    if not args:
        return Response("bad_input")
    
    return db.rename_network(user_id, args[0], new_name)


# Deletes a network and all related devices from the dzatabase
@app.post("/networks/<network_id>/delete")
@returns_response_obj
@require_auth
def delete_network(user_id, network_id):

    args = to_ints([network_id])
    if not args:
        return Response("bad_input")
        
    return db.delete_network(user_id, args[0])


# Shares access to a network with another user
@app.post("/networks/<network_id>/share/<recipient_id>")
@returns_response_obj
@require_auth
def share_network(user_id, network_id, recipient_id):

    args = to_ints([user_id, recipient_id, network_id])
    if not args:
        return Response("bad_input")
    
    return db.grant_access(args[0], args[1], args[2])


# Shares access to a network with another user
@app.post("/daemon/<network_id>/share/<recipient_auth>")
@returns_response_obj
@require_auth
def share_network(user_id, network_id, recipient_id):

    args = to_ints([user_id, recipient_id, network_id])
    if not args:
        return Response("bad_input")
    
    return db.grant_access(args[0], args[1], args[2])


# Gets the ID and name of all users
@app.get("/users/<network_id>")
@returns_response_obj
@require_auth
def get_users(user_id, network_id):

    args = to_ints([network_id,])
    if not args:
        return Response("bad_input")

    return db.get_users_with_access(args[0])


# Retrieves the logged in user's settings json from the database
@app.get("/settings")
@returns_response_obj
@require_auth
def get_settings(user_id):

    return db.get_settings(user_id)


# Sets a user's settings for scanning and frontend preferences in the database
@app.put("/settings/set")
@returns_response_obj
@require_auth
def set_settings(user_id):

    settings = None
    try:
        settings = request.get_json()
    except:
        return Response("bad_input")
        
    return db.set_settings(user_id, settings)


# Retrieves basic information about all snapshots of a certain network in the databsase
@app.get("/networks/<network_id>/snapshots")
@returns_response_obj
@require_auth
def get_snapshots(user_id, network_id):

    args = to_ints([network_id])
    if not args:
        return Response("bad_input")
        
    return db.get_snapshots(user_id, args[0])


# Retrieves a specific snapshot of a network at a point in time
@app.get("/networks/<network_id>/snapshots/<timestamp>")
@returns_response_obj
@require_auth
def get_snapshot(user_id, network_id, timestamp):

    args = to_ints([network_id, timestamp])
    if not args:
        return Response("bad_input")
        
    return db.get_all_devices(user_id, args[0], args[1]) 


# Retrieves the salt associated with a certain username
@app.get("/users/<username>/salt")
@returns_response_obj
def get_salt(username):

    salt = db.get_salt_by_username(username)
    if not salt:
        return Response("no_user")
    
    return Response("success", content={"salt" : salt})


if __name__=="__main__":
    app.run(host=app.config["SERVER_URI"], port=app.config["SERVER_PORT"])

