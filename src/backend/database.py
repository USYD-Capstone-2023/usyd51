import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

from datetime import datetime

class PostgreSQL_database:

    err_codes = {"success" : ("Success.", 200),
                "no_network" : ("Network with given ID is not present in the database.", 500),
                "malformed_network" : ("Provided network information is malformed.", 500),
                "save_network" : ("Encountered error saving network information.", 500),
                "save_device" : ("Encountered error saving device information.", 500),
                "malformed_settings" : ("Provded settings information is malformed.", 500),
                "no_snapshot" : ("There is no snapshot of the given network taken at the given time.", 500),
                "no_user" : ("User with given ID is not present in the database.", 500),
                "db_error" : ("The database server encountered an error, please try again.", 500)}

    def __init__(self, database, user, password):

        self.db = database
        self.user = user
        self.password = password

        # Creates database if it doesnt exist, creates table if they dont exist
        if not self.__init_db() or not self.__init_tables():

            print("[ERR ] Fatal error occurred while initialising database. Exitting...")
            sys.exit(-1)


    # Passes the given query to the database, retrieves result or commits if required
    def query(self, query, params, res=False):

        response = None
        conn = None
        try:
            # Open db connection
            conn = psycopg2.connect(database=self.db, user=self.user, password=self.password, host="localhost")
            cur = conn.cursor()
            # Run query
            cur.execute(query, params)

            # Retrieve result or commit changes if required
            if res:
                response = cur.fetchall()
            else:
                conn.commit()

            cur.close()
            conn.close()

        except Exception as e:
            print(e)
            print(f"{query} % {params}")
            if conn:
                cur.close()
                conn.close()

            return False
        
        if res:
            return response
        
        return True

    
    # ---------------------------------------------- NETWORKS ------------------------------------------ #
        

    # TODO check name input
    def save_network(self, network):

        # Ensures given network data is correctly formed
        required = ["network_id", "ssid", "gateway_mac", "name", "devices", "timestamp"]
        for req in required:
            if req not in network.keys():
                return self.err_codes["malformed_network"]
            
        devices = network["devices"]
        # Ensures given device data is well formed
        required = ["mac", "ip", "mac_vendor", "os_family", "os_vendor", "os_type", "hostname", "parent", "ports"]
        for device in devices.values():
            for req in required:
                if req not in device.keys():
                    return self.err_codes["malformed_device"]
                
        id = network["network_id"]
        # Registers a new network with a unique ID if the given id doesnt exist or is invalid
        if id == -1 or not self.__contains_network(id):
            id = self.get_next_network_id()
            if id == False:
                return self.err_codes["db_error"]
            
            network["network_id"] = id
            if not self.__register_network(network):
                return self.err_codes["db_error"]
                
                
        timestamp = network["timestamp"]
        # Adds timestamp to database if it doesn't already exist
        if not self.__contains_snapshot(id, timestamp):
            if not self.add_snapshot(id, timestamp):
                return self.err_codes["db_error"]
        
        if not self.__save_devices(id, devices, timestamp):
            return self.err_codes["db_error"]
        return self.err_codes["success"]
    

    # Adds a network to the database if it doesnt already exist.
    def __register_network(self, network):

        query = """
                INSERT INTO networks (id, gateway_mac, name, ssid)
                VALUES (%s, %s, %s, %s);
                """
        
        params = (network["network_id"],
                    network["gateway_mac"],
                    network["name"],
                    network["ssid"],)
        
        return self.query(query, params)
    
    # Gets the next available unique network id
    def get_next_network_id(self):

        query = """
                SELECT id
                FROM networks;
                """

        response = self.query(query, (), res=True)
        if response == False:
            return False
        
        if response == None:
            return 0

        next = -1
        for r in response:
            next = max(next, r[0])

        return next + 1
    

    # Deletes a network from the database
    def delete_network(self, network_id):

        if not self.__contains_network(network_id):
            return self.err_codes["no_network"]

        params = (network_id,)

        query = """
                DELETE FROM devices
                WHERE network_id = %s;
                """
        
        if not self.query(query, params):
            return self.err_codes["db_error"]

        query = """
                DELETE FROM snapshots
                WHERE network_id = %s;
                """
        
        if not self.query(query, params):
            return self.err_codes["db_error"]

        query = """
                DELETE FROM networks
                WHERE id = %s;
                """

        if not self.query(query, params):
            return self.err_codes["db_error"]

        return self.err_codes["success"]


    # Checks if the current network exists in the database
    def __contains_network(self, network_id):

        query = """
                SELECT 1
                FROM networks
                WHERE id = %s;
                """
        
        params = (network_id,)

        response = self.query(query, params, res=True)

        return response != None and len(response) > 0


    # Returns a list of all networks
    def get_networks(self):

        query = """
                SELECT id, gateway_mac, name, ssid
                FROM networks;
                """

        responses = self.query(query, (), res=True)

        if responses == None:
            return self.err_codes["no_network"]
        
        out = []
        for resp in responses:
            net_dict = {"id" : resp[0],
                        "gateway_mac": resp[1],
                        "name": resp[2],
                        "ssid": resp[3],
                        "n_alive" : len(self.get_all_devices(resp[0]))}
            
            out.append(net_dict)
            
        return out, 200


    # Returns all devices associated with a specific network
    def get_network(self, network_id):

        if not self.__contains_network(network_id):
            return self.err_codes["no_network"]

        query = """
                SELECT id, gateway_mac, name, ssid
                FROM networks
                WHERE id = %s;
                """
        
        params = (network_id,)

        network_info = self.query(query, params, res=True)[0]

        if not network_info:
            return self.err_codes["db_error"]

        network = {"id" : network_info[0],
                   "gateway_mac" : network_info[1],
                   "name" : network_info[2],
                   "ssid" : network_info[3],
                   "n_alive" : len(self.get_all_devices(network_id))} 

        return network, 200


    # Allows users to rename a network and all device data
    def rename_network(self, network_id, new_name):

        if not self.__contains_network(network_id):
            return self.err_codes["no_network"]

        query = """
                UPDATE networks
                SET name = %s
                WHERE id = %s;
                """
        
        params = (new_name, network_id,)

        if not self.query(query, params):
            return self.err_codes["db_error"]
        
        return self.err_codes["success"]



    # ---------------------------------------------- DEVICES ------------------------------------------- #
        

    # Gets all devices stored in the network corresponding to the gateway's MAC address
    def get_all_devices(self, network_id, timestamp=None):

        if not self.__contains_network(network_id):
            return self.err_codes["no_network"]
        
        if timestamp == None:
            timestamp = self.__get_most_recent_timestamp(network_id)
        
        else:
            if not self.__contains_snapshot(network_id, timestamp):
                return self.err_codes["no_snapshot"]

        query = """
                SELECT mac, ip, mac_vendor, os_family, os_vendor, os_type, hostname, parent, ports
                FROM devices
                WHERE network_id = %s AND timestamp = %s;
                """
        
        params = (network_id, timestamp,)

        responses = self.query(query, params, res=True)
        if responses == False:
            return self.err_codes["db_error"]
        
        devices = []
        for device in responses:
            devices.append(
                {"mac" : device[0], 
                "ip" : device[1], 
                "mac_vendor" : device[2], 
                "os_family" : device[3], 
                "os_vendor" : device[4], 
                "os_type" : device[5], 
                "hostname" : device[6], 
                "parent" : device[7], 
                "ports" : device[8]})

        return devices, 200
    

    # Saves given devices to database at the given timestamp
    def __save_devices(self, network_id, devices, timestamp):

        query = """
                UPDATE snapshots
                SET
                    n_alive = %s
                WHERE network_id = %s and timestamp = %s;
                """
        
        params = (len(devices.keys()), network_id, timestamp,)

        if not self.query(query, params):
            return False
            
        for device in devices.values():
            if not self.__add_device(network_id, device, timestamp):
                return False

        return True


    # Adds a device into the database
    def __add_device(self, network_id, device, timestamp):

        if not self.__contains_snapshot(network_id, timestamp):
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
        
        return self.query(query, params)


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
        
        return self.query(query, params)


    # --------------------------------------------- SNAPSHOTS ------------------------------------------ #


    # Retrieves the timestamp of a network's most recent scan
    def __get_most_recent_timestamp(self, network_id):
        
        query = """
                SELECT DISTINCT timestamp
                FROM snapshots
                WHERE network_id = %s;
                """
        
        params = (network_id,)

        response = self.query(query, params, res=True)

        if not response or len(response) == 0:
            return None

        max = response[0][0]
        for resp in response:
            dt = datetime.fromtimestamp(resp[0])
            max = max if datetime.fromtimestamp(max) > dt else resp[0]

        return max


    # Adds a snapshot for a given network ID and timestamp
    def add_snapshot(self, network_id, timestamp):

        query = """
                INSERT INTO snapshots (
                    network_id,
                    timestamp,
                    n_alive)
                VALUES (%s, %s, 0);
                """
        
        params = (network_id, timestamp,)

        if not self.query(query, params):
            return False
        
        return True
        

    # Returns an array of all timestamp-device_count pairs for a certain network.
    # There is a pair corresponding to each individual time a scan has been conducted.
    def get_snapshots(self, network_id):

        if not self.__contains_network(network_id):
            return self.err_codes["no_network"]

        query = """
                SELECT timestamp, n_alive
                FROM snapshots
                WHERE network_id = %s;
                """
        
        params = (network_id,)

        responses = self.query(query, params, res=True)
        if responses == False:
            return self.err_codes["db_error"]

        out = []
        for response in responses:
            r_dict = {}
            r_dict["timestamp"] = response[0]
            r_dict["n_alive"] = response[1]
            out.append(r_dict)

        return out, 200


    # Checks if a certain snapshot exists for the given network
    def __contains_snapshot(self, network_id, timestamp):

        query = """
                SELECT 1
                FROM snapshots
                WHERE network_id = %s and timestamp = %s;
                """
        
        params = (network_id, timestamp,)

        response = self.query(query, params, res=True)
        return response != None and len(response) > 0
        

    # ---------------------------------------------- SETTINGS ------------------------------------------ #


    # Retrieves a user's settings from database
    def get_settings(self, user_id):

        if not self.__contains_settings(user_id):
            return self.err_codes["no_user"]

        query = """
                SELECT *
                FROM settings
                WHERE user_id = %s;
                """
        
        params = (user_id,)

        response = self.query(query, params, res=True)
        if not response or len(response) == 0:
            return self.err_codes["db_error"]

        keys = ["user_id", "TCP", "UDP", "ports", "run_ports", "run_os", "run_hostname", 
                "run_mac_vendor", "run_trace", "run_vertical_trace", "defaultView",
                "defaultNodeColour", "defaultEdgeColour", "defaultBackgroundColour"]

        out = {}
        for i in range(len(keys)):
            out[keys[i]] = response[0][i]

        return out, 200


    # Updates an existing entry in the settings table
    def set_settings(self, user_id, settings):

        if type(settings) != dict:
            return self.err_codes["malformed_settings"]
        
        # TODO - add format checking for frontend settings and port string
        #          Entry : type
        require = {"TCP" : bool,
                   "UDP" : bool,
                   "ports" : str,
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

        # Ensures format and types in settings json is correct
        for req in require.keys():
            if req not in settings.keys() or type(settings[req]) != require[req]:
                return self.err_codes["malformed_settings"]
            

        query, params = ""
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

        if not self.query(query, params):
            return self.err_codes["db_error"]
        
        return self.err_codes["success"]


    # Checks if there is an entry in the settings table for the current user.
    # TODO - temporary, will be changed when I add users
    def __contains_settings(self, user_id):

        query = """
                SELECT 1
                FROM settings
                WHERE user_id = %s;
                """
        
        params = (user_id,)

        response = self.query(query, params, res=True)
        return response != None and len(response) > 0


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
            conn = psycopg2.connect(database="postgres", user=self.user, password=self.password, host="localhost")
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            # Create Cursor Object
            cur = conn.cursor()
            cur.execute(query, params)

            res = cur.fetchone()

            # Creates database if it doesnt exist
            if res == None or len(res) == 0:

                query = """
                        CREATE DATABASE %s;
                        """ % self.db

                cur.execute(query)
                conn.commit()

            cur.close()
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
                            (id INTEGER PRIMARY KEY,
                            gateway_mac TEXT,
                            name TEXT,
                            ssid TEXT);
                        """


        init_settings = """
                        CREATE TABLE IF NOT EXISTS settings
                            (user_id INTEGER PRIMARY KEY,
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
                            defaultBackgroundColour TEXT NOT NULL
                            )
                        """

        init_snapshots = """
                        CREATE TABLE IF NOT EXISTS snapshots
                            (network_id INTEGER REFERENCES networks (id),
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


        val =  self.query(init_networks, ())
        val &= self.query(init_snapshots, ())
        val &= self.query(init_devices, ())
        val &= self.query(init_settings, ())

        if val:
            return True
        
        return False
