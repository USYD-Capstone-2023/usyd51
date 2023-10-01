import requests
import unittest
import sys
import time
import jwt
from datetime import datetime, timedelta
from subprocess import Popen

sys.path.append("../backend")

from config import TestingConfig
from database import PostgreSQL_database as pdb

# Start test db server and wait for it to be running
proc = Popen("python ../backend/db_server.py testing", shell=True)
time.sleep(2)

# TODO - Need to reset the database before each run if we want to test anything more than auth, 
# having psycopg2 transaction issues
class auth_tests(unittest.TestCase):

    # Tests that the signup system works with valid input, and doesnt produce duplicates
    def test_signup(self):
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup",
                            json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        assert res.status_code in [pdb.err_codes["success"][1], pdb.err_codes["dup_user"][1]]
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                            json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        assert res.status_code == pdb.err_codes["dup_user"][1]


    # Checks that the login system works for an existing user, and that it returns an auth token
    def test_login(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", 
                            json={"username" : "sam", "password" : "passwd"})
        
        assert res.status_code == pdb.err_codes["success"][1]
        assert len(res.content) > 0


    # -------------------------------------- /networks --------------------------------------


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting the networks list
    # without an auth token.
    def test_get_networks_no_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks")
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting the networks list 
    # with a malformed or invalid auth token.
    def test_get_networks_invalid_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks", 
                           headers={"Auth-Token" : "this is an invalid auth token"})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting the networks list 
    # with an expired auth token.
    def test_get_networks_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server gives access to the networks list (even though it obviously wont process it 
    # correctly in this context), when a valid auth token is given.
    def test_get_networks_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", 
                            json={"username" : "sam", "password" : "passwd"})
        
        token = res.content.decode("utf-8")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code != pdb.err_codes["no_access"][1]


    # -------------------------------------- /networks/<id> --------------------------------------


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting a specific network's 
    # information without an auth token.
    def test_get_network_no_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0")
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting a specific network's 
    # information with a malformed or invalid auth token.
    def test_get_network_invalid_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0", 
                           headers={"Auth-Token" : "this is an invalid auth token"})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting a specific network's 
    # information with an expired auth token.
    def test_get_network_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server gives access to a specific network's information (even though it obviously
    # wont process it correctly in this context), when a valid auth token is given.
    def test_get_network_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", 
                            json={"username" : "sam", "password" : "passwd"})
        
        token = res.content.decode("utf-8")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code != pdb.err_codes["no_access"][1]


    # -------------------------------------- /network/<id>/devices --------------------------------------


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting a network's device list
    # without an auth token.
    def test_get_network_devices_no_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/devices")
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting a network's device list
    # with a malformed or invalid auth token.
    def test_get_network_devices_invalid_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/devices", 
                           headers={"Auth-Token" : "this is an invalid auth token"})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting a network's device list 
    # with an expired auth token.
    def test_get_network_devices_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/devices", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server gives access to a network's device list (even though it obviously wont process
    # it correctly in this context), when a valid auth token is given.
    def test_get_network_devices_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", 
                            json={"username" : "sam", "password" : "passwd"})
        
        token = res.content.decode("utf-8")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/devices", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code != pdb.err_codes["no_access"][1]


    # -------------------------------------- /networks/add --------------------------------------


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to add a new network
    # without an auth token.
    def test_add_network_no_auth(self):
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/add")
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to add a new network 
    # with a malformed or ivalid auth token.
    def test_add_network_invalid_auth(self):
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/add", 
                           headers={"Auth-Token" : "this is an invalid auth token"})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to add a new network 
    # with an expired auth token.
    def test_add_network_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/add", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server gives access to add a new network (even though it obviously wont process 
    # it correctly in this context), when a valid auth token is given.
    def test_add_network_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", 
                      json={"username" : "sam", "password" : "passwd"})
        
        token = res.content.decode("utf-8")
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/add", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code != pdb.err_codes["no_access"][1]


    # -------------------------------------- /networks/<id>/rename/<name> --------------------------------------


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to rename a network 
    # without an auth token.
    def test_rename_no_auth(self):
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/rename/new_name")
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to rename a network 
    # with a malformed or invalid auth token.
    def test_rename_invalid_auth(self):
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/rename/new_name", 
                           headers={"Auth-Token" : "this is an invalid auth token"})
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to rename a network 
    # with an expired auth token.
    def test_rename_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/rename/new_name", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server gives access to rename a network (even though it obviously wont process it 
    # correctly in this context), when a valid auth token is given.
    def test_rename_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", 
                      json={"username" : "sam", "password" : "passwd"})
        
        token = res.content.decode("utf-8")
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/rename/new_name", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code != pdb.err_codes["no_access"][1]


    # -------------------------------------- /networks/<id>/delete --------------------------------------


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to delete a network 
    # without an auth token.
    def test_delete_no_auth(self):
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/delete")
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to delete a network 
    # with a malformed or invalid auth token.
    def test_delete_invalid_auth(self):
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/delete", 
                           headers={"Auth-Token" : "this is an invalid auth token"})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to delete a network 
    # with an expired auth token.
    def test_delete_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/delete", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server gives access to delete a network (even though it obviously wont process it 
    # correctly in this context), when a valid auth token is given.
    def test_delete_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", 
                      json={"username" : "sam", "password" : "passwd"})
        
        token = res.content.decode("utf-8")
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/delete", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code != pdb.err_codes["no_access"][1]


    # -------------------------------------- /settings --------------------------------------


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting a user's settings
    # without an auth token.
    def test_get_settings_no_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/settings")
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting a user's settings
    # with a malformed or invalid auth token.
    def test_get_settings_invalid_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/settings", 
                           headers={"Auth-Token" : "this is an invalid auth token"})
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting a user's settings
    # with an expired auth token.
    def test_get_settings_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/settings", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server gives access to a user's settings (even though it obviously wont process
    # it correctly in this context), when a valid auth token is given.
    def test_get_settings_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", 
                      json={"username" : "sam", "password" : "passwd"})
        
        token = res.content.decode("utf-8")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/settings", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code != pdb.err_codes["no_access"][1]


    # -------------------------------------- /settings/set --------------------------------------


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to set a user's 
    # settings without an auth token.
    def test_set_settings_no_auth(self):
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/settings/set")
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to set a user's 
    # settings with a malformed or invalid auth token.
    def test_set_settings_invalid_auth(self):
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/settings/set", 
                           headers={"Auth-Token" : "this is an invalid auth token"})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to set a user's 
    # settings with an expired auth token.
    def test_set_settings_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/settings/set", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server gives access to set a user's settings (even though it obviously wont
    # process it correctly in this context), when a valid auth token is given.
    def test_set_settings_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", 
                      json={"username" : "sam", "password" : "passwd"})
        
        token = res.content.decode("utf-8")
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/settings/set", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code != pdb.err_codes["no_access"][1]


    # -------------------------------------- /networks/<id>/snapshots --------------------------------------


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to view a networ's snapshot
    # list without an auth token.
    def test_get_snapshots_no_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots")
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to view a networ's snapshot
    # list with a malformed or invalid auth token.
    def test_get_snapshots_invalid_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots", 
                           headers={"Auth-Token" : "this is an invalid auth token"})
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting to view a networ's snapshot
    # list with an expired auth token.
    def test_get_snapshots_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server gives access to view a networ's snapshot list(even though it obviously wont process
    # it correctly in this context), when a valid auth token is given.
    def test_get_snapshots_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", 
                      json={"username" : "sam", "password" : "passwd"})
        
        token = res.content.decode("utf-8")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code != pdb.err_codes["no_access"][1]


    # -------------------------------------- /networks/<id>/snapshots/<timestamp> --------------------------------------


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting a specific network 
    # snapshot without an auth token.
    def test_get_snapshot_no_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots/100000")
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting a specific network 
    # snapshot with a malformed or invalid auth token.
    def test_get_snapshot_invalid_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots/100000", 
                           headers={"Auth-Token" : "this is an invalid auth token"})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server returns HTTP 401 / Unauthorized access when requesting a specific network 
    # snapshot with an expired auth token.
    def test_get_snapshot_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots/100000", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code == pdb.err_codes["no_access"][1]


    # Checks that the server gives access to a specific network snapshot (even though it obviously wont
    # process it correctly in this context), when a valid auth token is given.
    def test_get_snapshot_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", 
                      json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", 
                      json={"username" : "sam", "password" : "passwd"})
        
        token = res.content.decode("utf-8")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots/100000", 
                           headers={"Auth-Token" : token})
        
        assert res.status_code != pdb.err_codes["no_access"][1]


if __name__ == "__main__":
    unittest.main()

proc.kill()