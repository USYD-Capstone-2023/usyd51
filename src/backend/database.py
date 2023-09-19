import psycopg2, sys

from datetime import datetime

class PostgreSQL_database:

    def __init__(self, database, user, password):

        self.db = database
        self.user = user
        self.password = password

        if not self.init_tables():

            print("[ERR ] Fatal error occurred while initialising database. Exitting...")
            sys.exit(-1)

    # Passes the given query to the database, retrieves result or commits if required
    def query(self, querystring, res=False):

        response = None
        conn = None
        try:
            # Open Database Connection
            conn = psycopg2.connect(database=self.db, user=self.user, password=self.password, host="localhost")
            # Create Cursor Object
            cur = conn.cursor()
            # Run query
            cur.execute(querystring)

            # Check Response
            if res:
                response = cur.fetchall()
            else:
                # Commit Query
                conn.commit()

        except Exception as e:
            print(e)
            print(querystring)

        finally:
            if conn:
                cur.close()
                conn.close()

        return response


    # Adds a network to the database if it doesnt already exist.
    def register_network(self, network):

        # Ensures network format is correct
        required = ["network_id", "ssid", "gateway_mac", "name"]

        for req in required:
            if req not in network.keys():
                return False

        query = """
                INSERT INTO networks (id, gateway_mac, name, ssid)
                VALUES (%s, '%s', '%s', '%s');
                """  % (
                    network["network_id"],
                    network["gateway_mac"],
                    network["name"],
                    network["ssid"])
        
        self.query(query)
        return True
    
    
    # Saves given devices to database at the given timestamp
    def save_devices(self, network_id, devices, ts):
    
        # Ensures given data is well formed
        required = ["mac", "ip", "mac_vendor", "os_family", "os_vendor", "os_type", "hostname", "parent", "ports"]
        for device in devices.values():
            for req in required:
                if req not in device.keys():
                    return False
                
            self.add_device(network_id, device, ts)

        return True
    

    # Deletes a network from the database
    def delete_network(self, network_id):

        if not self.contains_network(network_id):
            return False

        query = """
                DELETE FROM devices
                WHERE network_id = %s;
                """ % (network_id)

        self.query(query)

        query = """
                DELETE FROM networks
                WHERE id = %s;
                """ % (network_id)

        self.query(query)

        return True


    # Checks if the current network exists in the database
    def contains_network(self, network_id):

        query = """
                SELECT 1
                FROM networks
                WHERE id = %s;
                """ % (network_id)

        response = self.query(query, res=True)

        return response != None and len(response) > 0


    # Returns a list of all networks
    def get_networks(self):

        query = """
                SELECT id, gateway_mac, name, ssid
                FROM networks;
                """

        response = self.query(query, res=True)

        return [{"id" : x[0], "gateway_mac": x[1], "name": x[2], "ssid": x[3]} for x in response]


    # Returns all devices associated with a specific network
    def get_network(self, network_id):


        query = """
                SELECT id, gateway_mac, name, ssid
                FROM networks
                WHERE id = %s;
                """ % (network_id)

        network_info = self.query(query, res=True)[0]

        network = {
            "id" : network_info[0],
            "gateway_mac" : network_info[1],
            "name" : network_info[2],
            "ssid" : network_info[3]} 

        return network
    

    # Allows users to rename a network and all its data
    def rename_network(self, network_id, new_name):

        if not self.contains_network(network_id):
            return False

        query = """
                UPDATE networks
                SET name = '%s'
                WHERE id = %s;
                """ % (new_name, network_id)

        self.query(query)
        return True


    # Adds a device into the database
    def add_device(self, network_id, device, ts):

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
                VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, %s);
                """ % (
                    device["mac"], 
                    device["ip"], 
                    device["mac_vendor"], 
                    device["hostname"], 
                    device["os_type"],
                    device["os_vendor"], 
                    device["os_family"], 
                    device["parent"], 
                    device["ports"],
                    network_id, 
                    ts)

        self.query(query)

    
    # Updates the most recent version of the database to add new data
    def update_device(self, network_id, device):

        ts = self.get_most_recent_ts(network_id)

        query = """
                UPDATE devices
                SET
                    mac = '%s', 
                    ip = '%s', 
                    mac_vendor = '%s', 
                    hostname = '%s', 
                    os_type = '%s', 
                    os_vendor = '%s', 
                    os_family = '%s', 
                    parent = '%s', 
                    ports = '%s',
                WHERE network_id = %s and timestamp = %s;
                """ % (
                    device["mac"], 
                    device["ip"], 
                    device["mac_vendor"], 
                    device["hostname"], 
                    device["os_type"],
                    device["os_vendor"], 
                    device["os_family"], 
                    device["parent"], 
                    device["ports"],
                    network_id, 
                    ts)
        
        self.query(query)



    # Checks if a device is in the database. Devices are stored by MAC address,
    # and thus we check if the db contains the MAC.
    def contains_mac(self, network_id, mac, ts):
        
        query = """
                SELECT 1
                FROM devices 
                WHERE mac = '%s' AND network_id = %s AND timestamp = %s;
                """ % (mac, network_id, ts)

        response = self.query(query, res=True)
        return response != None and len(response) > 0 != None


    # Retrieves the timestamp of a network's most recent scan
    def get_most_recent_ts(self, network_id):
        
        query = """
                SELECT DISTINCT timestamp
                FROM devices
                WHERE network_id = %s;
                """ % (network_id)

        response = self.query(query, res=True)

        if response == None or len(response) == 0:
            return None

        max = response[0][0]
        for resp in response:
            dt = datetime.fromtimestamp(resp[0])
            max = max if datetime.fromtimestamp(max) > dt else resp[0]

        return max


    # Gets all devices stored in the network corresponding to the gateway's MAC address
    def get_all_devices(self, network_id, ts=None):

        if ts == None:
            ts = self.get_most_recent_ts(network_id)

        query = """
                SELECT mac, ip, mac_vendor, os_family, os_vendor, os_type, hostname, parent, ports
                FROM devices
                WHERE network_id = %s AND timestamp = %s;
                """ % (network_id, ts)

        responses = self.query(query, res=True)
        
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

        return devices


    # Gets the next available unique network id
    def get_next_network_id(self):

        query = """
                SELECT id
                FROM networks
                """

        response = self.query(query, res=True)

        next = -1
        for r in response:
            next = max(next, r[0])

        return next + 1


    def get_settings(self, user_id):

        query = """
                SELECT *
                FROM settings
                WHERE user_id = '%s';
                """ % (user_id)

        response = self.query(query, res=True)
        if len(response) == 0:
            return None

        keys = ["user_id", "TCP", "UDP", "ports", "run_ports", "run_os", "run_hostname", 
                "run_mac_vendor", "run_trace", "run_vertical_trace", "defaultView",
                "defaultNodeColour", "defaultEdgeColour", "defaultBackgroundColour"]

        out = {}
        for i in range(len(keys)):
            out[keys[i]] = response[0][i]

        return out


    def set_settings(self, user_id, settings):

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
                VALUES (%s, %s, %s, '%s', %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', '%s');
                """ % (
                    user_id,
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
                    settings["defaultBackgroundColour"]
                    )

        self.query(query)

        return True


    def contains_settings(self, user_id):

        query = """
                SELECT 1
                FROM settings
                WHERE user_id = %s;
                """ % (user_id)

        response = self.query(query, res=True)
        return response != None and len(response) > 0 != None


    # Setup tables if it doesn't exist
    # Currently using rouster MAC as PK for networks, need to find something much better
    def init_tables(self):

        # Main Tables
        # query_users = """CREATE TABLE IF NOT EXISTS users
        #                 (id TEXT PRIMARY KEY NOT NULL,
        #                 email TEXT NOT NULL,
        #                 password TEXT NOT NULL,
        #                 company TEXT NOT NULL);
        #                 """

        query_networks = """
                        CREATE TABLE IF NOT EXISTS networks
                            (id INTEGER PRIMARY KEY,
                            gateway_mac TEXT,
                            name TEXT,
                            ssid TEXT);
                        """


        query_settings = """
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


        query_devices = """
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
                            network_id INTEGER REFERENCES networks (id),
                            timestamp INTEGER NOT NULL,
                            CONSTRAINT id PRIMARY KEY (mac, network_id, timestamp));
                        """

        # query_layer3s = """CREATE TABLE IF NOT EXISTS layer3s
        #                 (id SERIAL PRIMARY KEY NOT NULL,
        #                 ip TEXT NOT NULL,
        #                 hostname TEXT,
        #                 human_name TEXT,
        #                 num_ports NUMBER,
        #                 ports FOREIGN KEY (id) REFERENCES layer3_ports,
        #                 vendor TEXT);
        #                 """

        # query_wirelessaps = """CREATE TABLE IF NOT EXISTS wirelessaps
        #                 (id SERIAL PRIMARY KEY NOT NULL,
        #                 ip TEXT NOT NULL,
        #                 hostname TEXT,
        #                 human_name TEXT,
        #                 devices FOREIGN KEY (id) REFERENCES wireless_devices,
        #                 port FOREIGN KEY (id) REFERENCES layer3,
        #                 vendor TEXT);
        #                 """
        # Join tables
        query_alive = """
                    CREATE TABLE IF NOT EXISTS alive
                        (id SERIAL PRIMARY KEY NOT NULL,
                        ip TEXT NOT NULL,
                        mac TEXT NOT NULL,
                        first_seen TIMESTAMP,
                        last_check TIMESTAMP,
                        last_online TIMESTAMP);
                    """

        # query_layer3_ports = """CREATE TABLE IF NOT EXISTS layer3_ports
        #             (id SERIAL PRIMARY KEY NOT NULL,
        #             port_name TEXT NOT NULL,
        #             mac TEXT NOT NULL,
        #             layer3 FORIEGN KEY (id) REFERENCES layer3s,
        #             device FORIEGN KEY (id) REFERENCES devices;
        #             """

        # run all the database queries
        # self.query(query_users)
        self.query(query_networks)
        self.query(query_devices)
        self.query(query_settings)
        # self.query(query_layer3s)
        # self.query(query_wirelessaps)
        self.query(query_alive)
        # self.query(query_layer3_ports)

        return True
