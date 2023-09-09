import sqlite3, sys

from device import Device

class SQLiteDB:

    def __init__(self, database):

        self.connection = None
        self.cursor = None
        self.db = database

        if not self.init_tables():

            print("[ERR ] Fatal error occurred while initialising database. Exitting...")
            sys.exit(-1)


    def query(self, querystring, params=(), res=False):

        response = None
        conn = None
        try:
            ## Open Database Connection
            conn = sqlite3.connect(self.db)

            # Create Cursor Object
            cur = conn.cursor()

            # Run query
            cur.execute(querystring, params)

            # Check Response
            if res:
                response = cur.fetchall()
            else:
                # Commit Query
                conn.commit()

        except sqlite3.Error as error:
            print(error)
            print(querystring)

        finally:
            if conn:
                cur.close()
                conn.close()

        return response


    # Adds a network to the database if it doesnt already exist.
    def register_network(self, gateway_mac, ssid, name):

        if not self.contains_network(gateway_mac):
            print("[INFO] Registering new network...")

            query = """
                    INSERT INTO networks (name, gateway_mac, ssid)
                    VALUES (?, ?, ?);
                    """
            
            params = (name, gateway_mac, ssid,)

            self.query(query, params)


    # Deletes a network from the database
    def delete_network(self, network_name):

        if not self.contains_network(network_name):
            return False

        query = """
                DELETE FROM networks
                WHERE name = ?;
                """

        params = (network_name,)

        self.query(query, params)
        return True


    # Checks if the current network exists in the database
    def contains_network(self, network_name):

        query = """
                SELECT 1
                FROM networks
                WHERE name = ?;
                """

        params = (network_name,)

        response = self.query(query, params, res=True)

        return response != None and len(response) > 0


    # Returns a list of all networks
    def get_network_names(self):

        query = """
                SELECT *
                FROM networks
                """

        response = self.query(query, res=True)

        return [{"name": x[0], "gateway_mac": x[1], "ssid": x[2]} for x in response]


    # Returns all devices associated with a specific network
    def get_network(self, network_name):

        query = """
                SELECT ip, mac, mac_vendor, hostname, os_type, os_vendor, os_family, parent
                FROM devices JOIN networks ON devices.network_name = networks.name
                WHERE networks.name = ?;
                """ 
        params = (network_name,)

        responses = self.query(query, params, res=True)

        # { mac : Device }
        devices = {}

        # Converts all responses into Device objects
        for response in responses:
            new_device = Device(response[0], response[1])
            new_device.mac_vendor = response[2]
            new_device.hostname = response[3]
            new_device.os_type = response[4]
            new_device.os_vendor = response[5]
            new_device.os_family = response[6]
            new_device.parent = response[7]

            devices[response[0]] = new_device

        return devices


    # Allows users to rename a network and all its data
    def rename_network(self, old_name, new_name):

        if not self.contains_network(old_name) or self.contains_network(new_name):
            return False

        query = """
                UPDATE devices
                SET network_name = ?
                WHERE network_name = ?;
                """

        params = (new_name, old_name,)

        self.query(query, params)

        query = """
                UPDATE networks
                SET name = ?
                WHERE name = ?;
                """

        self.query(query, params)
        return True


    # Adds a device into the database
    def add_device(self, network_name, device):

        query = """
                INSERT INTO devices(mac, ip, mac_vendor, hostname, os_type, os_vendor, os_family, parent, network_name)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);
                """

        params = (device.mac, device.ip, device.mac_vendor, device.hostname, device.os_type,
                 device.os_vendor, device.os_family, device.parent, network_name,)

        self.query(query, params)


    # Checks if a device is in the database. Devices are stored by MAC address, and thus we check if the db contains the MAC.
    def contains_mac(self, network_name, mac):
        
        query = """
                SELECT 1
                FROM devices 
                WHERE mac = ? AND network_name = ?;
                """

        params = (mac, network_name,)

        response = self.query(query, params, res=True)
        return response != None and len(response) > 0 != None


    # Gets all devices stored in the network corresponding to the gateway's MAC address
    def get_all_devices(self, network_name):

        query = """
                SELECT ip, mac, mac_vendor, hostname, os_type, os_vendor, os_family, parent
                FROM devices
                WHERE network_name = ?;
                """

        params = (network_name,)

        responses = self.query(query, params, res=True)

        # { mac : Device }
        devices = {}

        # Converts all responses into Device objects
        for response in responses:
            new_device = Device(response[0], response[1])
            new_device.mac_vendor = response[2]
            new_device.hostname = response[3]
            new_device.os_type = response[4]
            new_device.os_vendor = response[5]
            new_device.os_family = response[6]
            new_device.parent = response[7]

            devices[response[0]] = new_device

        return devices


    # Retrieves a device from the database by a combination of it's MAC address and the gateway's MAC address
    def get_device(self, network_name, mac):

        query = """
                SELECT ip, mac, mac_vendor, hostname, os_type, os_vendor, os_family, parent
                FROM devices
                WHERE network_name = ? AND mac = ?;
                """
            
        params = (network_name, mac,)

        response = self.query(query, params, res=True)

        if len(response) == 0 or len(response[0]) < 8:
            return None

        response = response[0]

        # Creates Device object from response
        new_device = Device(response[0], response[1])
        new_device.mac_vendor = response[2]
        new_device.hostname = response[3]
        new_device.os_type = response[4]
        new_device.os_vendor = response[5]
        new_device.os_family = response[6]
        new_device.parent = response[7]

        return new_device


    # Saves an existing device back to the database after it has been changed.
    def save_device(self, network_name, device):

        query = """
                UPDATE devices
                SET mac = ?,
                    ip = ?,
                    mac_vendor = ?,
                    hostname = ?,
                    os_type = ?,
                    os_vendor = ?,
                    os_family = ?,
                    parent = ?
                WHERE network_name = ? AND mac = ?;
                """

        params = (device.mac, device.ip, device.mac_vendor,
                  device.hostname, device.os_type, device.os_vendor,
                  device.os_family, device.parent, network_name, device.mac,)

        self.query(query, params)


    # Setup tables if it doesn't exist
    # Currently using rouster MAC as PK for networks, need to find something much better
    def init_tables(self):


        try:

            conn = sqlite3.connect(self.db)
        
        except sqlite3.Error as e:

            print(e)
            return False

        # Main Tables
        # query_users = """CREATE TABLE IF NOT EXISTS users
        #                 (id TEXT PRIMARY KEY NOT NULL,
        #                 email TEXT NOT NULL,
        #                 password TEXT NOT NULL,
        #                 company TEXT NOT NULL);
        #                 """

        query_networks = """
                        CREATE TABLE IF NOT EXISTS networks
                            (name TEXT TEXT PRIMARY KEY,
                            gateway_mac TEXT NOT NULL,
                            ssid TEXT);
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
                            network_name TEXT REFERENCES networks (name) ON DELETE CASCADE,
                            CONSTRAINT id PRIMARY KEY (mac, network_name));
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
        # self.query(query_layer3s)
        # self.query(query_wirelessaps)
        self.query(query_alive)
        # self.query(query_layer3_ports)

        return True
