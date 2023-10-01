import requests
import unittest
import sys
import time
import jwt
from datetime import datetime, timedelta
from subprocess import Popen

sys.path.append("../backend")

from config import TestingConfig

proc = Popen("python ../backend/db_server.py testing", shell=True)
time.sleep(2)

class auth_tests(unittest.TestCase):

    #  dup and valid
    def test_signup(self):
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        assert res.status_code in [200, 507]


    def test_login(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", json={"username" : "sam", "password" : "passwd"})
        assert res.status_code == 200
        assert len(res.content) > 0


    # -------------------------------------- /networks --------------------------------------


    def test_get_networks_no_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks")
        assert res.status_code == 401


    def test_get_networks_invalid_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks", headers={"Auth-Token" : "this is an invalid auth token"})
        assert res.status_code == 401


    def test_get_networks_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks", headers={"Auth-Token" : token})
        assert res.status_code == 401


    def test_get_networks_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", json={"username" : "sam", "password" : "passwd"})
        token = res.content.decode("utf-8")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks", headers={"Auth-Token" : token})
        assert res.status_code != 401


    # -------------------------------------- /networks/<id> --------------------------------------


    def test_get_network_no_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0")
        assert res.status_code == 401


    def test_get_network_invalid_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0", headers={"Auth-Token" : "this is an invalid auth token"})
        assert res.status_code == 401


    def test_get_network_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0", headers={"Auth-Token" : token})
        assert res.status_code == 401


    def test_get_network_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", json={"username" : "sam", "password" : "passwd"})
        token = res.content.decode("utf-8")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0", headers={"Auth-Token" : token})
        assert res.status_code != 401


    # -------------------------------------- /network/<id>/devices --------------------------------------


    def test_get_network_devices_no_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/devices")
        assert res.status_code == 401


    def test_get_network_devices_invalid_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/devices", headers={"Auth-Token" : "this is an invalid auth token"})
        assert res.status_code == 401


    def test_get_network_devices_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/devices", headers={"Auth-Token" : token})
        assert res.status_code == 401


    def test_get_network_devices_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", json={"username" : "sam", "password" : "passwd"})
        token = res.content.decode("utf-8")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/devices", headers={"Auth-Token" : token})
        assert res.status_code != 401


    # -------------------------------------- /networks/add --------------------------------------


    def test_add_network_no_auth(self):
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/add")
        assert res.status_code == 401


    def test_add_network_invalid_auth(self):
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/add", headers={"Auth-Token" : "this is an invalid auth token"})
        assert res.status_code == 401


    def test_add_network_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/add", headers={"Auth-Token" : token})
        assert res.status_code == 401


    def test_add_network_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", json={"username" : "sam", "password" : "passwd"})
        token = res.content.decode("utf-8")
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/add", headers={"Auth-Token" : token})
        assert res.status_code != 401


    # -------------------------------------- /networks/<id>/rename/<name> --------------------------------------


    def test_rename_no_auth(self):
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/rename/new_name")
        assert res.status_code == 401


    def test_rename_invalid_auth(self):
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/rename/new_name", headers={"Auth-Token" : "this is an invalid auth token"})
        assert res.status_code == 401


    def test_rename_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/rename/new_name", headers={"Auth-Token" : token})
        assert res.status_code == 401


    def test_rename_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", json={"username" : "sam", "password" : "passwd"})
        token = res.content.decode("utf-8")
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/rename/new_name", headers={"Auth-Token" : token})
        assert res.status_code != 401


    # -------------------------------------- /networks/<id>/delete --------------------------------------


    def test_delete_no_auth(self):
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/delete")
        assert res.status_code == 401


    def test_delete_invalid_auth(self):
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/delete", headers={"Auth-Token" : "this is an invalid auth token"})
        assert res.status_code == 401


    def test_delete_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/delete", headers={"Auth-Token" : token})
        assert res.status_code == 401


    def test_delete_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", json={"username" : "sam", "password" : "passwd"})
        token = res.content.decode("utf-8")
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/delete", headers={"Auth-Token" : token})
        assert res.status_code != 401


    # -------------------------------------- /settings --------------------------------------


    def test_get_settings_no_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/settings")
        assert res.status_code == 401


    def test_get_settings_invalid_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/settings", headers={"Auth-Token" : "this is an invalid auth token"})
        assert res.status_code == 401


    def test_get_settings_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/settings", headers={"Auth-Token" : token})
        assert res.status_code == 401


    def test_get_settings_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", json={"username" : "sam", "password" : "passwd"})
        token = res.content.decode("utf-8")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/settings", headers={"Auth-Token" : token})
        assert res.status_code != 401


    # -------------------------------------- /settings/set --------------------------------------


    def test_set_settings_no_auth(self):
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/settings/set")
        assert res.status_code == 401


    def test_set_settings_invalid_auth(self):
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/settings/set", headers={"Auth-Token" : "this is an invalid auth token"})
        assert res.status_code == 401


    def test_set_settings_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/settings/set", headers={"Auth-Token" : token})
        assert res.status_code == 401


    def test_set_settings_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", json={"username" : "sam", "password" : "passwd"})
        token = res.content.decode("utf-8")
        res = requests.put("http://" + TestingConfig.SERVER_URI + ":5000/settings/set", headers={"Auth-Token" : token})
        assert res.status_code != 401


    # -------------------------------------- /networks/<id>/snapshots --------------------------------------


    def test_get_snapshots_no_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots")
        assert res.status_code == 401


    def test_get_snapshots_invalid_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots", headers={"Auth-Token" : "this is an invalid auth token"})
        assert res.status_code == 401


    def test_get_snapshots_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots", headers={"Auth-Token" : token})
        assert res.status_code == 401


    def test_get_snapshots_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", json={"username" : "sam", "password" : "passwd"})
        token = res.content.decode("utf-8")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots", headers={"Auth-Token" : token})
        assert res.status_code != 401


    # -------------------------------------- /networks/<id>/snapshots/<timestamp> --------------------------------------


    def test_get_snapshot_no_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots/100000")
        assert res.status_code == 401


    def test_get_snapshot_invalid_auth(self):
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots/100000", headers={"Auth-Token" : "this is an invalid auth token"})
        assert res.status_code == 401


    def test_get_snapshot_old_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        exp = (datetime.utcnow() - timedelta(minutes=1)).strftime("%d/%m/%Y/%H/%M/%S")
        token = jwt.encode({"user_id" : 0, "expiry" : exp}, TestingConfig.SECRET_KEY, algorithm="HS256")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots/100000", headers={"Auth-Token" : token})
        assert res.status_code == 401


    def test_get_snapshot_valid_auth(self):
        requests.post("http://" + TestingConfig.SERVER_URI + ":5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
        res = requests.post("http://" + TestingConfig.SERVER_URI + ":5000/login", json={"username" : "sam", "password" : "passwd"})
        token = res.content.decode("utf-8")
        res = requests.get("http://" + TestingConfig.SERVER_URI + ":5000/networks/0/snapshots/100000", headers={"Auth-Token" : token})
        assert res.status_code != 401





    # def test__no_auth(self):
    # def test__invalid_auth(self):
    # def test__old_auth(self):
    # def test__valid_auth(self):

        # res = requests.post("http://127.0.0.1:5000/login", json={"username" : "sam", "password" : "passwd"})
        # if res.status_code != 200:
        #     print(f"{res.content} {res.status_code}")

        # auth = res.content.decode("utf-8")
        # print("Auth token is: %s\n" % auth)

        # res = requests.post("http://127.0.0.1:5001/scan/-1", headers={"Auth-Token" : auth})
        # if res.status_code != 200:
        #     print(f"{res.content} {res.status_code}")

        # res = requests.get("http://127.0.0.1:5000/networks", headers={"Auth-Token" : auth})
        # if res.status_code != 200:
        #     print(f"{res.content} {res.status_code}")

        # print(res.content)


if __name__ == "__main__":
    unittest.main()

proc.kill()