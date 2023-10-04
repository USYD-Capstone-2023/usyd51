import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

from datetime import datetime

class PostgreSQL_database:

    # Standard error codes and messages
    err_codes = {"success" : ("Success.", 200),
                "no_network" : ("Network with given ID is not present in the database.", 500),
                "no_snapshot" : ("There is no snapshot of the given network taken at the given time.", 501),
                "no_user" : ("User with given ID is not present in the database.", 502),
                "malformed_network" : ("Provided network information is malformed.", 503),
                "malformed_settings" : ("Provided settings information is malformed.", 504),
                "malformed_device" : ("Provided device information is malformed.", 505),
                "malformed_user" : ("Provided user information is malformed.", 506),
                "dup_user" : ("A user with that username already exists.", 507),
                "db_error" : ("The database server encountered an error, please try again.", 508),
                "bad_input" : ("Input was not numeric.", 509),
                "no_access" : ("Current user does not have access to this resource.", 401)}


    def __init__(self, database, user, password):

        self.db = database
        self.user = user
        self.password = password

        # Creates database if it doesnt exist, creates table if they dont exist
        if not self.__init_db() or not self.__init_tables():

            print("[ERR ] Fatal error occurred while initialising database. Exitting...")
            sys.exit(-1)


    # Passes the given query to the database, retrieves result or commits if required
    def __query(self, query, params, res=False):

        response = None
        try:
            # Open db connection
            with psycopg2.connect(database=self.db, user=self.user, password=self.password, host="localhost") as conn:
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
        

    def save_network(self, user_id, network):

        if not type(user_id) == int:
            return *self.err_codes["bad_input"], None

        # Ensures given network data is correctly formed
        required = {"network_id" : int,
                    "ssid" : str,
                    "gateway_mac" : str,
                    "name" : str,
                    "devices" : dict,
                    "timestamp" : int}
        
        # Checks type and key of all attributes of the network
        for req in required.keys():
            if req not in network.keys() or type(network[req]) != required[req]:
                return *self.err_codes["malformed_network"], None
            
        # Ensures given device data is well formed
        devices = network["devices"]
        required = {"mac" : str,
                    "ip" : str,
                    "mac_vendor" : str,
                    "os_family" : str,
                    "os_vendor" : str,
                    "os_type" : str,
                    "hostname" : str,
                    "parent" : str,
                    "ports" : list}
        
        # Checks type and key of all attributes of each device
        for device in devices.values():
            for req in required.keys():
                if req not in device.keys() or type(device[req]) != required[req]:
                    return *self.err_codes["malformed_device"], None
                
        # Gets the next valid ID if the ID parameter is unset
        network_id = network["network_id"]
        if network_id == -1:
            network_id = self.__get_next_network_id()
            network["network_id"] = network_id
            
        # Adds a new network to the database if it doesnt exist
        res = self.validate_network_access(user_id, network_id)
        if res[1] == 500:
            if not self.__register_network(user_id, network):
                return *self.err_codes["db_error"], None

        elif res[1] == 401:
            return res                
                
        # Adds timestamp to database if it doesn't already exist
        timestamp = network["timestamp"]
        if not self.contains_snapshot(network_id, timestamp):
            if not self.__add_snapshot(network_id, timestamp):
                return *self.err_codes["db_error"], None
        
        # Saves all devices
        if not self.__save_devices(network_id, devices, timestamp):
            return *self.err_codes["db_error"], None
        
        if not self.__set_n_alive(network_id, len(devices)):
            return *self.err_codes["db_error"], None
        
        return *self.err_codes["success"], network_id
    

    # Adds a network to the database
    def __register_network(self, user_id, network):

        query = """
                INSERT INTO networks (network_id, gateway_mac, name, ssid, n_alive, user_id)
                VALUES (%s, %s, %s, %s, %s, %s);
                """
        
        params = (network["network_id"],
                  network["gateway_mac"],
                  network["name"],
                  network["ssid"],
                  len(network["devices"]),
                  user_id,)
        
        return self.__query(query, params)
    

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
        next = -1
        for r in response:
            next = max(next, r[0])

        return next + 1
    

    # Deletes a network from the database
    def delete_network(self, user_id, network_id):

        if not type(user_id) == int | type(network_id) == int:
            return *self.err_codes["bad_input"], None

        # Checks requested network exists, and current user can access it
        res = self.validate_network_access(user_id, network_id)
        if res[1] != 200:
            return res

        params = (network_id,)

        # Deletes all devices related to the network
        query = """
                DELETE FROM devices
                WHERE network_id = %s;
                """
        
        if not self.__query(query, params):
            return *self.err_codes["db_error"], None

        # Deletes all snapshots related to the network
        query = """
                DELETE FROM snapshots
                WHERE network_id = %s;
                """
        
        if not self.__query(query, params):
            return *self.err_codes["db_error"], None

        # Deletes the network
        query = """
                DELETE FROM networks
                WHERE network_id = %s;
                """

        if not self.__query(query, params):
            return *self.err_codes["db_error"], None

        return *self.err_codes["success"], None


    # Checks if the current network exists in the database
    def validate_network_access(self, user_id, network_id):

        if not type(user_id) == int | type(network_id) == int:
            return *self.err_codes["bad_input"], None
        
        if network_id == -1:
            return *self.err_codes["success"], None

        query = """
                SELECT user_id
                FROM networks
                WHERE network_id = %s;
                """
        
        params = (network_id,)

        response = self.__query(query, params, res=True)

        if not response or len(response) == 0:
            return *self.err_codes["no_network"], None
        
        if response[0][0] != user_id:
            return *self.err_codes["no_access"], None
        
        return *self.err_codes["success"], None


    # Returns a list of all networks accessible to the given user
    def get_networks(self, user_id):

        if not type(user_id) == int:
            return *self.err_codes["bad_input"], None
        
        query = """
                SELECT network_id, gateway_mac, name, ssid, n_alive
                FROM networks
                WHERE user_id = %s;
                """
        
        params = (user_id,)

        responses = self.__query(query, params, res=True)
        if responses == False:
            return *self.err_codes["db_error"], None
        
        # Return empty array when the database is empty
        if responses == None:
            return *self.err_codes["success"], []
        
        # Formats output if the query is completed successfully
        out = []
        for resp in responses:

            net_dict = {"network_id"  : resp[0],
                        "gateway_mac" : resp[1],
                        "name"        : resp[2],
                        "ssid"        : resp[3],
                        "n_alive"     : resp[4],
                        "timestamp"   : self.__get_most_recent_timestamp(resp[0])}
            
            out.append(net_dict)
            
        return *self.err_codes["success"], out


    # Returns all basic information associated with a network
    def get_network(self, user_id, network_id):

        if not type(user_id) == int | type(network_id) == int:
            return *self.err_codes["bad_input"], None
        
        # Checks requested network exists, and current user can access it
        res = self.validate_network_access(user_id, network_id)
        if res[1] != 200:
            return res

        query = """
                SELECT network_id, gateway_mac, name, ssid, n_alive
                FROM networks
                WHERE network_id = %s and user_id = %s;
                """
        
        params = (network_id, user_id,)

        network_info = self.__query(query, params, res=True)[0]
        if not network_info:
            return *self.err_codes["db_error"], None

        # Formats output if the query is completed successfully
        network = {"network_id" : network_info[0],
                   "gateway_mac" : network_info[1],
                   "name" : network_info[2],
                   "ssid" : network_info[3],
                   "n_alive" : network_info[4]} 

        return *self.err_codes["success"], network


    # Allows users to rename a network and all device data
    def rename_network(self, user_id, network_id, new_name):

        if not type(user_id) == int | type(network_id) == int | new_name == "":
            return *self.err_codes["bad_input"], None

        # Checks requested network exists, and current user can access it
        res = self.validate_network_access(user_id, network_id)
        if res[1] != 200:
            return res

        query = """
                UPDATE networks
                SET name = %s
                WHERE network_id = %s;
                """
        
        params = (new_name, network_id,)

        if not self.__query(query, params):
            return *self.err_codes["db_error"], None
        
        return *self.err_codes["success"], None


    # ---------------------------------------------- DEVICES ------------------------------------------- #
        

    # Gets all devices stored in the network corresponding to the gateway's MAC address
    def get_all_devices(self, user_id, network_id, timestamp=None):

        if not type(user_id) == int | type(network_id) == int:
            return *self.err_codes["bad_input"], None
        
        # Checks requested network exists, and current user can access it
        res = self.validate_network_access(user_id, network_id)
        if res[1] != 200:
            return res
        
        # Retrieves most recent snapshot of the network if no timestamp is provided
        if timestamp == None:
            timestamp = self.__get_most_recent_timestamp(network_id)
        
        else:
            # Errors if the given timestamp is not recorded
            if not self.contains_snapshot(network_id, timestamp):
                return *self.err_codes["no_snapshot"], None

        query = """
                SELECT mac, ip, mac_vendor, os_family, os_vendor, os_type, hostname, parent, ports
                FROM devices
                WHERE network_id = %s AND timestamp = %s;
                """
        
        params = (network_id, timestamp,)

        responses = self.__query(query, params, res=True)
        if responses == False:
            return *self.err_codes["db_error"], None
        
        # Formats output if the query is completed successfully
        devices = []
        for device in responses:

            port_str = device[8].replace("{", "").replace("}", "").split(",")
            port_ls = []
            if len(port_str) > 0:
                port_ls = [int(x) for x in port_ls]
                
            devices.append(
                {"mac" : device[0], 
                "ip" : device[1], 
                "mac_vendor" : device[2], 
                "os_family" : device[3], 
                "os_vendor" : device[4], 
                "os_type" : device[5], 
                "hostname" : device[6], 
                "parent" : device[7], 
                "ports" : port_ls})

        return *self.err_codes["success"], devices
    

    # Saves given devices to database at the given timestamp
    def __save_devices(self, network_id, devices, timestamp):

        valid = 0
        # Adds all entered devices to database  
        for device in devices.values():
            if self.__add_device(network_id, device, timestamp):
                # Counts only devices that were successfully added to the database
                valid += 1
            
        # Updates related snapshot with new n_alive attribute
        query = """
                UPDATE snapshots
                SET
                    n_alive = %s
                WHERE network_id = %s and timestamp = %s;
                """
        
        params = (valid, network_id, timestamp,)

        if not self.__query(query, params):
            return False

        return True


    # Adds a device into the database
    def __add_device(self, network_id, device, timestamp):

        # Checks that requested snapshot exists
        if not self.contains_snapshot(network_id, timestamp):
            return False

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


    # NOT IMPLEMENTED YET, GOING TO BE USED FOR INCREMENTAL SAVING AND DISPLAYING OF SCANS
    # Updates the most recent version of a device to add new data
    def __update_device(self, network_id, device):

        timestamp = self.__get_most_recent_timestamp(network_id)

        query = """
                UPDATE devices
                SET
                    mac = %s, 
                    ip = %s, 
                    mac_vendor = %s, 
                    hostname = %s, 
                    os_type = %s, 
                    os_vendor = %s, 
                    os_family = %s, 
                    parent = %s, 
                    ports = %s,
                WHERE network_id = %s and timestamp = %s;
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


    # --------------------------------------------- SNAPSHOTS ------------------------------------------ #


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

        if not self.__query(query, params):
            return False
        
        return True
        

    # Returns an array of all timestamp-device_count pairs for a certain network.
    # There is a pair corresponding to each individual time a scan has been conducted.
    def get_snapshots(self, user_id, network_id):

        if not type(user_id) == int | type(network_id) == int:
            return *self.err_codes["bad_input"], None
        
        # Checks requested network exists, and current user can access it
        res = self.validate_network_access(user_id, network_id)
        if res[1] != 200:
            return res

        query = """
                SELECT timestamp, n_alive
                FROM snapshots
                WHERE network_id = %s;
                """
        
        params = (network_id,)

        responses = self.__query(query, params, res=True)
        if responses == False:
            return *self.err_codes["db_error"], None

        # Formats output and returns if query is completed successfully
        out = []
        for response in responses:
            r_dict = {}
            r_dict["timestamp"] = response[0]
            r_dict["n_alive"] = response[1]
            out.append(r_dict)

        return *self.err_codes["success"], out


    # Checks if a certain snapshot exists for the given network
    def contains_snapshot(self, network_id, timestamp):

        if not type(network_id) == int:
            return *self.err_codes["bad_input"], None
        
        query = """
                SELECT 1
                FROM snapshots
                WHERE network_id = %s and timestamp = %s;
                """
        
        params = (network_id, timestamp,)

        response = self.__query(query, params, res=True)
        return response != None and len(response) > 0
        

    # ---------------------------------------------- SETTINGS ------------------------------------------ #


    # Retrieves a user's settings from database
    def get_settings(self, user_id):

        if not type(user_id) == int:
            return *self.err_codes["bad_input"], None

        # Checks that requested user exists in the database
        if not self.__contains_settings(user_id):
            return *self.err_codes["no_user"], None

        query = """
                SELECT user_id,
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
                       defaultBackgroundColour
                FROM settings
                WHERE user_id = %s;
                """
        
        params = (user_id,)

        response = self.__query(query, params, res=True)
        if not response or len(response) == 0:
            return *self.err_codes["db_error"], None
        
        port_str = response[0][3].replace("{", "").replace("}", "").split(",")
        port_ls = []
        if len(port_str) > 0:
            port_ls = [int(x) for x in port_str]

        # Formats output and returns if query is completed successfully
        out = {"user_id" : response[0][0],
               "TCP" : response[0][1],
               "UDP" : response[0][2],
               "ports" : port_ls,
               "run_ports" : response[0][4],
               "run_os" : response[0][5],
               "run_hostname" : response[0][6],
               "run_mac_vendor" : response[0][7],
               "run_trace" : response[0][8],
               "run_vertical_trace" : response[0][9],
               "defaultView" : response[0][10],
               "defaultNodeColour" : response[0][11],
               "defaultEdgeColour" : response[0][12],
               "defaultBackgroundColour" : response[0][13]}

        return *self.err_codes["success"], out


    # Sets the scan and preference settings for a given user
    def set_settings(self, user_id, settings):

        if not type(user_id) == int:
            return *self.err_codes["bad_input"], None

        # Ensures input type is correct
        if type(settings) != dict:
            return *self.err_codes["malformed_settings"], None
        
        # TODO - add format checking for frontend settings and port list
        #          Entry : type
        required = {"TCP" : bool,
                   "UDP" : bool,
                   "ports" : list,
                   "run_ports" : bool,
                   "run_os" : bool,
                   "run_hostname" : bool,
                   "run_mac_vendor" : bool,
                   "run_trace" : bool,
                   "run_vertical_trace" : bool,
                   "defaultView" : str,
                   "defaultNodeColour" : str,
                   "defaultEdgeColour" : str,
                   "defaultBackgroundColour" : str}

        # Ensures format and typing in settings json is correct
        for req in required.keys():
            if req not in settings.keys() or type(settings[req]) != required[req]:
                return *self.err_codes["malformed_settings"], None
            

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
            
            params = (user_id,
                      settings["TCP"],
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
                    settings["defaultBackgroundColour"],
                    user_id,)

        if not self.__query(query, params):
            return *self.err_codes["db_error"], None
        
        return *self.err_codes["success"], None


    # Checks if there is an entry in the settings table for the current user.
    # TODO - temporary, will be changed when I add users
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


    def contains_user(self, username):

        query = """
                SELECT 1
                FROM users
                WHERE username = %s;
                """
        
        params = (username,)

        response = self.__query(query, params, res=True)
        return response != None and len(response) > 0
    

    def get_user_by_login(self, user):

        require = ["username", "password"]

        for req in require:
            if req not in user.keys():
                return *self.err_codes["malformed_user"], None

        query = """SELECT user_id, username, password, email
                   FROM users
                   WHERE username = %s AND password = %s;"""
        
        params = (user["username"], user["password"],)

        user_dict = self.__query(query, params, res=True)
        if not user_dict:
            return *self.err_codes["no_user"], None
        
        user = {"user_id" : user_dict[0][0],
                "username" : user_dict[0][1],
                "password" : user_dict[0][2],
                "email" : user_dict[0][3]}

        return *self.err_codes["success"], user
    

    def get_user_by_id(self, user_id):

        if not type(user_id) == int:
            return *self.err_codes["malformed_user"], None

        query = """SELECT user_id, username, password, email
                   FROM users
                   WHERE user_id = %s;"""
        
        params = (user_id,)

        user_dict = self.__query(query, params, res=True)
        if not user_dict:
            return *self.err_codes["no_user"], None
        
        user = {"user_id" : user_dict[0][0],
                "username" : user_dict[0][1],
                "password" : user_dict[0][2],
                "email" : user_dict[0][3]}

        return *self.err_codes["success"], user
    
    
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
        next = -1
        for r in response:
            next = max(next, r[0])

        return next + 1


    def add_user(self, user):

        require = ["username", "password", "email"]

        for req in require:
            if req not in user.keys():
                return *self.err_codes["malformed_user"], None
            
        if self.contains_user(user["username"]):
            return *self.err_codes["dup_user"], None

        query = """
                INSERT INTO users
                    (user_id,
                    username,
                    password,
                    email)
                VALUES (%s, %s, %s, %s);
                """
        
        params = (self.__get_next_user_id(), user["username"], user["password"], user["email"])

        if not self.__query(query, params):
            return *self.err_codes["db_error"], None
        
        return *self.err_codes["success"], None


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
        res = None
        try:
            # Open Database Connection
            with psycopg2.connect(database="postgres", user=self.user, password=self.password, host="localhost") as conn:
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

        except Exception as e:

            print(e)
            return False
        
        return True


    # Setup tables if it doesn't exist
    # Currently using rouster MAC as PK for networks, need to find something much better
    def __init_tables(self):

        init_networks = """
                        CREATE TABLE IF NOT EXISTS networks
                            (network_id INTEGER PRIMARY KEY,
                            user_id INTEGER REFERENCES users (user_id),
                            gateway_mac TEXT,
                            name TEXT,
                            ssid TEXT,
                            n_alive INTEGER);
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
                        email TEXT NOT NULL);              
                    """



        val = self.__query(init_users, ())
        val &=  self.__query(init_networks, ())
        val &= self.__query(init_snapshots, ())
        val &= self.__query(init_devices, ())
        val &= self.__query(init_settings, ())

        return val