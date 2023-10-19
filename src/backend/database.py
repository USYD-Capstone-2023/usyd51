import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

from response import Response
from datetime import datetime
from Crypto.Hash import SHA256

class PostgreSQL_database:
    
    network_format = {"network_id"  : int,
                      "ssid"        : str,
                      "gateway_mac" : str,
                      "name"        : str,
                      "timestamp"   : int,
                      "devices"     : dict}

    device_format = {"mac"        : str,
                     "ip"         : str,
                     "mac_vendor" : str,
                     "os_family"  : str,
                     "os_vendor"  : str,
                     "os_type"    : str,
                     "hostname"   : str,
                     "parent"     : str,
                     "ports"      : list}

    settings_format = {"TCP"                     : bool,
                       "UDP"                     : bool,
                       "ports"                   : list,
                       "run_ports"               : bool,
                       "run_os"                  : bool,
                       "run_hostname"            : bool,
                       "run_mac_vendor"          : bool,
                       "run_trace"               : bool,
                       "run_vertical_trace"      : bool,
                       "defaultView"             : str,
                       "defaultNodeColour"       : str,
                       "defaultEdgeColour"       : str,
                       "defaultBackgroundColour" : str}
    
    default_settings = {"TCP"                     : True,
                        "UDP"                     : True, 
                        "ports"                   : [22,23,80,443],
                        "run_ports"               : True,
                        "run_os"                  : False,
                        "run_hostname"            : True,
                        "run_mac_vendor"          : True,
                        "run_trace"               : True,
                        "run_vertical_trace"      : True,
                        "defaultView"             : "cluster",
                        "defaultNodeColour"       : "0FF54A",
                        "defaultEdgeColour"       : "32FFAB",
                        "defaultBackgroundColour" : "320000"}

    user_format = {"user_id"  : int,
                   "username" : str,
                   "password" : str,
                   "email"    : str,
                   "salt"     : str}


    def __init__(self, database, user, password, host, port):

        self.db = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        # Creates database if it doesnt exist, creates table if they dont exist
        if not (self.__init_db() and self.__init_tables()):

            print("[ERR ] Fatal error occurred while initialising database. Exitting...")
            sys.exit(-1)


    # Passes the given query to the database, retrieves result or commits if required
    def __query(self, query, params, res=False):

        response = None
        try:
            # Open db connection
            with psycopg2.connect(database=self.db, user=self.user, password=self.password, host=self.host, port=self.port) as conn:
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

                with conn.cursor() as cur:
                    # Run query
                    cur.execute(query, params)

                    # Retrieve result or commit changes if required
                    if res:
                        response = cur.fetchall()
                    else:
                        conn.commit()

        except Exception as e:
            print(e)
            print(f"{query} % {params}")
            return False
        
        if res:
            return response
        
        return True

    
    # ---------------------------------------------- NETWORKS ------------------------------------------ #
        

    # Saves a network and all of its devices to the database
    def save_network(self, user_id, network, exists=False):

        if not isinstance(user_id, int):
            return Response("bad_input")

        # Checks type and key of all attributes of the network
        for key, datatype in self.network_format.items():
            if key not in network.keys() or not isinstance(network[key], datatype):
                return Response("malformed_network")
            
        # Checks type and key of all attributes of each device
        devices = network["devices"]
        for device in devices.values():
            for key, datatype in self.device_format.items():
                if key not in device.keys() or not isinstance(device[key], datatype):
                    return Response("malformed_device")
                
        # Gets the next valid ID if the ID parameter is unset
        network_id = network["network_id"]
        if network_id <= -1:
            network_id = self.__get_next_network_id()
            network["network_id"] = network_id
            
        # Adds a new network to the database if it doesnt exist
        res = self.validate_network_access(user_id, network_id)
        if res.status == 401:
            return res 

        # Attempts to add network if it doesnt already exist
        elif res.status == 500 and not self.__register_network(user_id, network):               
            return Response("db_error")

        # Adds timestamp to database if it doesn't already exist
        timestamp = network["timestamp"]
        if not self.contains_snapshot(network_id, timestamp):
            # Doesnt allow creation of new snapshot if running in update mode
            if exists:
                return Response("db_error")

            if not self.__add_snapshot(network_id, timestamp):
                return Response("db_error")
            
        # Saves all devices
        if not self.__save_devices(network_id, devices, timestamp):
            return Response("db_error")
        
        # Sets number of alive devices
        if not self.__set_n_alive(network_id, len(devices)):
            return Response("db_error")
        
        return Response("success", network_id)
    

    # Deletes a network from the database
    # TODO Probs broken havent looked at it in a long time, isnt implemented in frontend to test
    def delete_network(self, user_id, network_id):

        if not (isinstance(user_id, int) and isinstance(network_id, int)):
            return Response("bad_input")

        # Checks requested network exists, and current user can access it
        res = self.validate_network_access(user_id, network_id)
        if res.status != 200:
            return res

        params = (network_id,)

        # Deletes all devices related to the network
        query = """
                DELETE FROM devices
                WHERE network_id = %s;
                """
        
        if not self.__query(query, params):
            return Response("db_error")

        # Deletes all snapshots related to the network
        query = """
                DELETE FROM snapshots
                WHERE network_id = %s;
                """
        
        if not self.__query(query, params):
            return Response("db_error")

        # Deletes the network
        query = """
                DELETE FROM networks
                WHERE network_id = %s;
                """

        if not self.__query(query, params):
            return Response("db_error")

        return Response("success")
    

    # Checks if the current network exists in the database, and that the provided user has access
    def validate_network_access(self, user_id, network_id):

        if not (isinstance(user_id, int) and isinstance(network_id, int)):
            return Response("bad_input")
        
        # Implicitly has access, as network doesnt exist
        if network_id == -1:
            return Response("success")

        query = """
                SELECT user_id
                FROM access
                WHERE network_id = %s;
                """
        
        params = (network_id,)
        response = self.__query(query, params, res=True)

        if not response:
            return Response("no_network")
        
        for user in response:
            if user[0] == user_id:
                return Response("success")

        return Response("no_access")
        
    

    # Returns a list of all networks accessible to the given user
    def get_networks(self, user_id):

        if not isinstance(user_id, int):
            return Response("bad_input")
        
        attrs = "network_id, ssid, gateway_mac, name, n_alive"
        attrs_q = "".join(["networks.%s, " % x for x in attrs.split(", ")])[:-2]
        
        query = f"""
                SELECT {attrs_q}
                FROM networks JOIN access
                ON networks.network_id = access.network_id
                WHERE access.user_id = %s;
                """
        
        params = (user_id,)

        res = self.__query(query, params, res=True)
        if res == False:
            return Response("db_error")
        
        # Return empty array when the database is empty
        if res == None:
            return Response("success", [])
        
        # Formats output if the query is completed successfully
        out = []
        for network in res:
            net_dict = dict(zip(attrs.split(", "), network))
            net_dict["timestamp"] = self.__get_most_recent_timestamp(net_dict["network_id"])

            out.append(net_dict)
            
        return Response("success", out)


    # Returns all basic information associated with a network
    def get_network(self, user_id, network_id):

        if not (isinstance(user_id, int) and isinstance(network_id, int)):
            return Response("bad_input")
        
        # Checks requested network exists, and current user can access it
        res = self.validate_network_access(user_id, network_id)
        if res.status != 200:
            return res
        
        attrs = "network_id, gateway_mac, name, ssid, n_alive"

        query = f"""
                SELECT {attrs}
                FROM networks
                WHERE network_id = %s;
                """
        
        params = (network_id,)

        res = self.__query(query, params, res=True)[0]
        if not res:
            return Response("db_error")

        # Formats output if the query is completed successfully
        net_dict = dict(zip(attrs.split(", "), res))
        net_dict["timestamp"] = self.__get_most_recent_timestamp(net_dict["network_id"])

        return Response("success", net_dict)


    # Allows users to rename a network and all device data
    def rename_network(self, user_id, network_id, new_name):

        if not (isinstance(user_id, int) and isinstance(network_id, int)) or new_name == "":
            return Response("bad_input")

        # Checks requested network exists, and current user can access it
        res = self.validate_network_access(user_id, network_id)
        if res.status != 200:
            return res

        query = """
                UPDATE networks
                SET name = %s
                WHERE network_id = %s;
                """
        
        params = (new_name, network_id,)

        if not self.__query(query, params):
            return Response("db_error")
        
        return Response("success")
    

    # Adds a network to the database
    def __register_network(self, user_id, network):

        query = """
                INSERT INTO networks (network_id, gateway_mac, name, ssid, n_alive)
                VALUES (%s, %s, %s, %s, %s);
                """
        
        params = (network["network_id"],
                  network["gateway_mac"],
                  network["name"],
                  network["ssid"],
                  len(network["devices"]),)
        
        if not self.__query(query, params):
            return False
        
        # Gives the current user access to the network
        query = """
                INSERT INTO access (network_id, user_id)
                VALUES (%s, %s);
                """
        
        params = (network["network_id"],
                  user_id,)
        
        return self.__query(query, params)
    

    # Sets number of alive devices for the network
    def __set_n_alive(self, network_id, n_alive):

        query = """
                UPDATE networks
                SET
                    n_alive = %s
                WHERE network_id = %s;
                """
        
        params = (n_alive, network_id,)

        return self.__query(query, params)
    

    # Gets the next available unique network id
    def __get_next_network_id(self):

        # Gets the ID of all networks in the database
        query = """
                SELECT network_id
                FROM networks;
                """

        response = self.__query(query, (), res=True)
        # Case for when there are no networks in the database
        if not response:
            return 0

        # Searches for the maximum ID
        # TODO Make a generator for ids to more efficiently find the next id
        # TODO - SAM, remove the ability to define your own network id. Dumbest feature ive added 
        next = 0
        for r in response:
            next = max(next, r[0])

        return next + 1


    # ---------------------------------------------- DEVICES ------------------------------------------- #
        

    # Gets all devices stored in the network corresponding to the gateway's MAC address
    def get_all_devices(self, user_id, network_id, timestamp=None):

        if not (isinstance(user_id, int) and isinstance(network_id, int)):
            return Response("bad_input")
        
        # Checks requested network exists, and current user can access it
        res = self.validate_network_access(user_id, network_id)
        if res.status != 200:
            return res
        
        # Retrieves most recent snapshot of the network if no timestamp is provided
        if timestamp == None:
            timestamp = self.__get_most_recent_timestamp(network_id)
        
        # Errors if the given timestamp is not recorded
        elif not self.contains_snapshot(network_id, timestamp):
            return Response("no_snapshot")
            
        attrs = "mac, ip, mac_vendor, os_family, os_vendor, os_type, hostname, parent, ports"

        query = f"""
                SELECT {attrs}
                FROM devices
                WHERE network_id = %s AND timestamp = %s;
                """
        
        params = (network_id, timestamp,)

        res = self.__query(query, params, res=True)
        if res == False:
            return Response("db_error")
        
        # Formats output if the query is completed successfully
        devices = []
        for device in res:

            device_dict = dict(zip(attrs.split(", "), device))

            # formats ports into a list
            port_str = device_dict["ports"].replace("{", "").replace("}", "")
            port_ls = []
            if len(port_str) > 0:
                port_ls = [int(x) for x in port_str.split(",")]

            device_dict["ports"] = port_ls
            devices.append(device_dict)

        return Response("success", devices)
    

    # Checks if a device is contained in a certain snapshot of a network
    def contains_device(self, network_id, mac, timestamp):

        query = """
                SELECT 1
                FROM devices
                WHERE network_id = %s and mac = %s and timestamp = %s;
                """

        params = (network_id, mac, timestamp,)

        response = self.__query(query, params, res=True)
        return response != None and len(response) > 0
    

    # Saves given devices to database at the given timestamp
    def __save_devices(self, network_id, devices, timestamp):

        # Snapshot must be initialised before devices can be saved
        if not self.contains_snapshot(network_id, timestamp):
            return False

        added = 0
        valid = False
        # Adds all entered devices to database, or updates them if they already exist in this snapshot
        for device in devices.values():
            if self.contains_device(network_id, device["mac"], timestamp):
                valid = self.__update_device(network_id, device, timestamp)

            else:
                valid = self.__add_device(network_id, device, timestamp)
            
            # Counts only devices that were successfully added to the database
            added += 1 if valid else 0

        # Updates related snapshot with new n_alive attribute
        query = """
                UPDATE snapshots
                SET
                    n_alive = %s
                WHERE network_id = %s and timestamp = %s;
                """
        
        params = (added, network_id, timestamp,)

        return self.__query(query, params)


    # Adds a device into the database in a certain snapshot
    def __add_device(self, network_id, device, timestamp):

        query = """
                INSERT INTO devices (
                    mac, 
                    ip, 
                    mac_vendor, 
                    hostname, 
                    os_type, 
                    os_vendor, 
                    os_family, 
                    parent, 
                    ports,
                    network_id, 
                    timestamp)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
        
        params = (device["mac"], 
                  device["ip"], 
                  device["mac_vendor"], 
                  device["hostname"], 
                  device["os_type"],
                  device["os_vendor"], 
                  device["os_family"], 
                  device["parent"], 
                  device["ports"],
                  network_id, 
                  timestamp,)
        
        return self.__query(query, params)


    # Updates the most recent version of a device to add new data
    def __update_device(self, network_id, device, timestamp):

        # Checks that requested snapshot exists
        if not self.contains_snapshot(network_id, timestamp):
            return False

        query = """
                UPDATE devices
                SET
                    ip = %s, 
                    mac_vendor = %s, 
                    hostname = %s, 
                    os_type = %s, 
                    os_vendor = %s, 
                    os_family = %s, 
                    parent = %s, 
                    ports = %s
                WHERE network_id = %s and timestamp = %s and mac = %s;
                """
        
        params = (device["ip"], 
                  device["mac_vendor"], 
                  device["hostname"], 
                  device["os_type"],
                  device["os_vendor"], 
                  device["os_family"], 
                  device["parent"], 
                  device["ports"],
                  network_id, 
                  timestamp,
                  device["mac"])
        
        return self.__query(query, params)


    # --------------------------------------------- SNAPSHOTS ------------------------------------------ #


    # Returns an array of all timestamp-device_count pairs for a certain network.
    # There is a pair corresponding to each individual time a scan has been conducted.
    def get_snapshots(self, user_id, network_id):

        if not (isinstance(user_id, int) and isinstance(network_id, int)):
            return Response("bad_input")
        
        # Checks requested network exists, and current user can access it
        res = self.validate_network_access(user_id, network_id)
        if res.status != 200:
            return res
        
        attrs = "timestamp, n_alive"

        query = f"""
                SELECT {attrs}
                FROM snapshots
                WHERE network_id = %s;
                """
        
        params = (network_id,)

        responses = self.__query(query, params, res=True)
        if responses == False:
            return Response("db_error")

        # Formats output and returns if query is completed successfully
        out = []
        for response in responses:
            r_dict = dict(zip(attrs.split(", "), response))
            out.append(r_dict)

        return Response("success", out)


    # Checks if a certain snapshot exists for the given network
    def contains_snapshot(self, network_id, timestamp):

        if not (isinstance(network_id, int) and isinstance(timestamp, int)):
            return Response("bad_input")
        
        query = """
                SELECT 1
                FROM snapshots
                WHERE network_id = %s and timestamp = %s;
                """
        
        params = (network_id, timestamp,)

        response = self.__query(query, params, res=True)
        return response != None and len(response) > 0
    

    # Retrieves the timestamp of a network's most recent scan
    def __get_most_recent_timestamp(self, network_id):
        
        query = """
                SELECT DISTINCT timestamp
                FROM snapshots
                WHERE network_id = %s;
                """
        
        params = (network_id,)

        response = self.__query(query, params, res=True)

        if not response or len(response) == 0:
            return None

        # Gets the most recent from all retrieved timestamps
        max = response[0][0]
        for resp in response:
            dt = datetime.fromtimestamp(resp[0])
            max = max if datetime.fromtimestamp(max) > dt else resp[0]

        return max


    # Adds a snapshot for a given network ID and timestamp
    def __add_snapshot(self, network_id, timestamp):

        query = """
                INSERT INTO snapshots (
                    network_id,
                    timestamp,
                    n_alive)
                VALUES (%s, %s, 0);
                """
        
        params = (network_id, timestamp,)

        return self.__query(query, params)
        

    # ---------------------------------------------- SETTINGS ------------------------------------------ #


    # Retrieves a user's settings from database
    def get_settings(self, user_id):

        if not isinstance(user_id, int):
            return Response("bad_input")

        # Checks that requested user's settings exist in the database
        if not self.__contains_settings(user_id):
            return Response("no_user")

        attrs = "user_id, TCP, UDP, ports, run_ports, run_os, run_hostname, run_mac_vendor, " + \
                "run_trace, run_vertical_trace, defaultView, defaultNodeColour, defaultEdgeColour, " + \
                "defaultBackgroundColour"
        
        query = f"""
                SELECT {attrs}
                FROM settings
                WHERE user_id = %s;
                """
        
        params = (user_id,)

        response = self.__query(query, params, res=True)
        if not response or len(response) == 0:
            return Response("db_error")
        
        if len(response[0]) != len(attrs.split(", ")):
            return Response("malformed_settings")

        # Formats output and returns if query is completed successfully
        settings = dict(zip(attrs.split(", "), response[0]))
        try:
            # Formats port string into a list
            settings["ports"] = settings["ports"].replace("{", "").replace("}", "").split(",")
            settings["ports"] = [int(x) for x in settings["ports"]]
        except:
            return Response("malformed_settings")

        return Response("success", content=settings)


    # Sets the scan and preference settings for a given user
    def set_settings(self, user_id, settings):

        if not isinstance(user_id, int):
            return Response("bad_input")

        # Ensures input type is correct
        if type(settings) != dict:
            return Response("malformed_settings")
        
        # Ensures format and typing in settings json is correct
        for key, datatype in self.settings_format.items():
            if key not in settings.keys() or not isinstance(settings[key], datatype):
                #TODO - Check ports formats, frontend settings format
                return Response("malformed_settings")
            

        params = (settings["TCP"],
                  settings["UDP"], 
                  settings["ports"],
                  settings["run_ports"],
                  settings["run_os"],
                  settings["run_hostname"],
                  settings["run_mac_vendor"],
                  settings["run_trace"],
                  settings["run_vertical_trace"],
                  settings["defaultView"],
                  settings["defaultNodeColour"],
                  settings["defaultEdgeColour"],
                  settings["defaultBackgroundColour"],)
            
        # Create settings entry for user if they dont exist
        if not self.__contains_settings(user_id):

            query = """
                    INSERT INTO settings (
                        user_id,
                        TCP,
                        UDP, 
                        ports,
                        run_ports,
                        run_os,
                        run_hostname,
                        run_mac_vendor,
                        run_trace,
                        run_vertical_trace,
                        defaultView,
                        defaultNodeColour,
                        defaultEdgeColour,
                        defaultBackgroundColour)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
            
            params = (user_id, *params)

        # Update existing settings data if the user exists
        else:
            query = """
                    UPDATE settings
                    SET
                        TCP = %s,
                        UDP = %s, 
                        ports = %s,
                        run_ports = %s,
                        run_os = %s,
                        run_hostname = %s,
                        run_mac_vendor = %s,
                        run_trace = %s,
                        run_vertical_trace = %s,
                        defaultView = %s,
                        defaultNodeColour = %s,
                        defaultEdgeColour = %s,
                        defaultBackgroundColour = %s
                    WHERE user_id = %s;
                    """
            
            params = (*params, user_id)

        if not self.__query(query, params):
            return Response("db_error")
        
        return Response("success")


    # Checks if the database contains the given user's settings
    def __contains_settings(self, user_id):

        query = """
                SELECT 1
                FROM settings
                WHERE user_id = %s;
                """
        
        params = (user_id,)

        response = self.__query(query, params, res=True)
        return response != None and len(response) > 0


    # --------------------------------------------- USERS ------------------------------------------ #


    # Checks if the database contains the given username
    def contains_user(self, username):

        query = """
                SELECT 1
                FROM users
                WHERE username = %s;
                """
        
        params = (username,)

        response = self.__query(query, params, res=True)
        return response != None and len(response) > 0
    

    # Adds a user to the database
    def add_user(self, user):

        for key, datatype in self.user_format.items():

            if key == "user_id":
                continue

            if key not in user.keys() or not isinstance(user[key], datatype):
                return Response("malformed_user")
            
        if self.contains_user(user["username"]):
            return Response("dup_user")
        
        attrs = "user_id, username, password, email, salt"

        query = f"""
                INSERT INTO users ({attrs})
                VALUES (%s, %s, %s, %s, %s);
                """
        
        user_id = self.__get_next_user_id()
        params = (user_id, user["username"], user["password"], user["email"], user["salt"],)

        if not self.__query(query, params):
            return Response("db_error")

        res = self.set_settings(user_id, self.default_settings)
        if res.status != 200:
            return res

        return Response("success")
    

    # Gets a user by their username and password
    def get_user_by_login(self, username, password):

        if type(username) != str or type(password) != str:
            return Response("bad_input")
        
        attrs = "user_id, username, password, email, salt"

        query = f"""SELECT {attrs}
                   FROM users
                   WHERE username = %s AND password = %s;"""
        
        params = (username, password)

        res = self.__query(query, params, res=True)
        if not res:
            return Response("no_user")
        
        user_dict = dict(zip(attrs.split(", "), res[0]))
        return Response("success", content=user_dict)
    

    # Gets a user's information by their ID
    def get_user_by_id(self, user_id):

        if not isinstance(user_id, int):
            return Response("malformed_user")

        attrs = "user_id, username, password, email"

        query = f"""SELECT {attrs}
                   FROM users
                   WHERE user_id = %s;"""
        
        params = (user_id,)

        res = self.__query(query, params, res=True)
        if not res:
            return Response("no_user")
        
        user_dict = dict(zip(attrs.split(", "), res[0]))
        return Response("success", user_dict)
    

    # Retrieves the salt associated with a user
    def get_salt_by_username(self, username):

        query = """
                SELECT salt
                FROM users
                WHERE username = %s;
                """
        
        params = (username,)

        res = self.__query(query, params, res=True)
        if not res or len(res) == 0:
            return None
        
        return res[0][0]


    # Retrieves all users from the database
    def get_users(self):

        args = "user_id, username, email"

        query = f"""
                SELECT {args}
                FROM users;
                """

        res = self.__query(query, (), res=True)
        if res == False:
            return Response("db_error")

        out = []
        for user in res:
            out.append(dict(zip(args.split(", "), user)))

        return Response("success", content=out)


    def get_users_with_access(self, network_id):

        query = f"""
                SELECT user_id
                FROM access
                WHERE network_id = %s;
                """

        params = (network_id,)

        with_access = self.__query(query, params, res=True)
        if with_access == False:
            return Response("db_error")

        all_users = self.get_users()
        if all_users.status != 200:
            return all_users

        all_users = all_users.content

        access = set()
        for user in with_access:
            access.add(user[0])

        out = {
            "shared"   : [],
            "unshared" : []
        }

        for user in all_users:
            # Dont add daemon account to list
            if user["user_id"] == 0:
                continue

            if user["user_id"] in access:
                out["shared"].append(user)

            else:
                out["unshared"].append(user)


        return Response("success", content=out)


    # Checks if a user has access to a given network
    def __has_access(self, user_id, network_id):

        query = """
                SELECT 1
                FROM networks JOIN access
                ON networks.network_id = access.network_id
                WHERE access.user_id = %s and networks.network_id = %s;
                """

        params = (user_id, network_id,)

        res = self.__query(query, params, res=True)
        return res and len(res) > 0
    

    # Gives a user access to the given network
    def grant_access(self, user_id, recipient_id, network_id):

        if not isinstance(user_id, int) or not isinstance(recipient_id, int) or not isinstance(network_id, int):
            return Response("bad_input")

        res = self.validate_network_access(user_id, network_id)
        if res.status != 200:
            return res 

        if self.__has_access(recipient_id, network_id):
            return Response("already_authorized")
        
        query = """
                INSERT INTO access
                    (user_id, network_id)
                VALUES (%s, %s);
                """

        params = (recipient_id, network_id,)

        if not self.__query(query, params):
            return Response("db_error")

        return Response("success")

    
    # Retrieves the next assignable user ID
    def __get_next_user_id(self):

        # Gets the ID of users in the database
        query = """
                SELECT user_id
                FROM users;
                """

        response = self.__query(query, (), res=True)
        # Case for when there are no networks in the database
        if not response:
            return 0

        # Searches for the maximum ID
        # TODO Make a generator for ids to more efficiently find the next id
        next = -1
        for r in response:
            next = max(next, r[0])

        return next + 1


    # --------------------------------------------- SETUP ------------------------------------------ #


    # Ensures that the database exists, creates it if not
    def __init_db(self):

        # Checks if database exists
        query = """
                SELECT 1
                FROM pg_catalog.pg_database
                WHERE datname = %s;
                """
        
        params = (self.db,)

        conn = None
        try:
            # Open Database Connection
            conn = psycopg2.connect(database="postgres", user=self.user, password=self.password, host=self.host, port=self.port)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            # Create Cursor Object
            with conn.cursor() as cur:
                cur.execute(query, params)

                res = cur.fetchone()

                # Creates database if it doesnt exist
                if res == None or len(res) == 0:

                    query = """
                            CREATE DATABASE %s;
                            """ % self.db

                    cur.execute(query)
                    conn.commit()

            conn.close()

        except Exception as e:

            print(e)
            if conn:
                conn.close()
            return False
        
        return True


    # Setup tables if it doesn't exist
    # Currently using rouster MAC as PK for networks, need to find something much better
    def __init_tables(self):

        init_networks = """
                        CREATE TABLE IF NOT EXISTS networks
                            (network_id INTEGER PRIMARY KEY,
                            gateway_mac TEXT,
                            name TEXT,
                            ssid TEXT,
                            n_alive INTEGER);
                        """

        init_access = """
                      CREATE TABLE IF NOT EXISTS access
                        (network_id INTEGER REFERENCES networks (network_id),
                        user_id INTEGER REFERENCES users (user_id),
                        PRIMARY KEY (network_id, user_id));
                      """ 


        init_settings = """
                        CREATE TABLE IF NOT EXISTS settings
                            (user_id INTEGER PRIMARY KEY REFERENCES users (user_id),
                            TCP BOOLEAN NOT NULL,
                            UDP BOOLEAN NOT NULL, 
                            ports TEXT NOT NULL,
                            run_ports BOOLEAN NOT NULL,
                            run_os BOOLEAN NOT NULL,
                            run_hostname BOOLEAN NOT NULL,
                            run_mac_vendor BOOLEAN NOT NULL,
                            run_trace BOOLEAN NOT NULL,
                            run_vertical_trace BOOLEAN NOT NULL,
                            defaultView TEXT NOT NULL,
                            defaultNodeColour TEXT NOT NULL,
                            defaultEdgeColour TEXT NOT NULL,
                            defaultBackgroundColour TEXT NOT NULL);
                        """

        init_snapshots = """
                        CREATE TABLE IF NOT EXISTS snapshots
                            (network_id INTEGER REFERENCES networks (network_id),
                            timestamp INTEGER NOT NULL,
                            n_alive INTEGER NOT NULL,
                            PRIMARY KEY (network_id, timestamp));
                        """

        init_devices = """
                        CREATE TABLE IF NOT EXISTS devices
                            (mac TEXT NOT NULL,
                            ip TEXT NOT NULL,
                            mac_vendor TEXT,
                            hostname TEXT,
                            os_type TEXT,
                            os_vendor TEXT,
                            os_family TEXT,
                            parent TEXT,
                            ports TEXT,
                            network_id INTEGER NOT NULL,
                            timestamp INTEGER NOT NULL,
                            FOREIGN KEY (network_id, timestamp) REFERENCES snapshots (network_id, timestamp),
                            PRIMARY KEY (mac, network_id, timestamp));
                        """
        
        init_users = """
                     CREATE TABLE IF NOT EXISTS users
                        (user_id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        email TEXT NOT NULL,
                        salt TEXT NOT NULL);              
                    """

        val = self.__query(init_users, ())
        val &=  self.__query(init_networks, ())
        val &= self.__query(init_snapshots, ())
        val &= self.__query(init_devices, ())
        val &= self.__query(init_settings, ())
        val &= self.__query(init_access, ())

        if not self.contains_user("daemon"):
            salt = "tesolkansdjonasdkjanbsdjnaflksndfkjnsdifjnsdkfgjnsfkgjn"
            hash = SHA256.new()
            hash.update(b"passwordtesolkansdjonasdkjanbsdjnaflksndfkjnsdifjnsdkfgjnsfkgjn")

            query = """
                    INSERT INTO users (user_id, username, password, email, salt)
                    VALUES (%s, %s, %s, %s, %s);
                    """
            
            params = ("0", "daemon", str(hash.hexdigest()), "email@address", salt)
            val &= self.__query(query, params)

        return val
    

    # --------------------------------------------- TESTING TEARDOWN ------------------------------------------ #

    # Drops the current db
    def drop_db(self):

        conn = None
        try:
            # Connects to default schema to drop the current database
            conn = psycopg2.connect(database="template1", user=self.user, password=self.password, host=self.host, port=self.port)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            with conn.cursor() as cur:
                # Run query
                cur.execute(f"DROP DATABASE {self.db};")
            conn.close()

        except Exception as e:
            print(e)
            if conn:
                conn.close()
            return False
        
        return True