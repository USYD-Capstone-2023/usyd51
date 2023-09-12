import sqlite3, sys

from device import Device
from datetime import datetime

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
    def register_network(self, id, gateway_mac, ssid, name):

        print("[INFO] Registering new network...")

        query = """
                INSERT INTO networks (id, gateway_mac, name, ssid)
                VALUES (?, ?, ?, ?);
                """
        
        params = (id, gateway_mac, name, ssid,)

        self.query(query, params)

        return True


    # Deletes a network from the database
    def delete_network(self, network_id):

        if not self.contains_network(network_id):
            return False

        query = """
                DELETE FROM networks
                WHERE id = ?;
                """

        params = (network_id,)

        self.query(query, params)

        query = """
                DELETE FROM devices
                WHERE network_id = ?;
                """

        self.query(query, params)
        return True


    # Checks if the current network exists in the database
    def contains_network(self, network_id):

        query = """
                SELECT 1
                FROM networks
                WHERE id = ?;
                """

        params = (network_id,)

        response = self.query(query, params, res=True)

        return response != None and len(response) > 0


    # Returns a list of all networks
    def get_network_names(self):

        query = """
                SELECT id, gateway_mac, name, ssid
                FROM networks
                """

        response = self.query(query, res=True)

        return [{"id" : x[0], "gateway_mac": x[1], "name": x[2], "ssid": x[3]} for x in response]


    # Returns all devices associated with a specific network
    def get_network(self, network_id):

        query = """
                SELECT ip, mac, mac_vendor, hostname, os_type, os_vendor, os_family, parent, timestamp
                FROM devices
                WHERE network_id = ?;
                """ 
        params = (network_id,)

        devices = self.query(query, params, res=True)

        query = """
                SELECT id, gateway_mac, name, ssid
                FROM networks
                WHERE id = ?;
                """ 

        network_info = self.query(query, params, res=True)[0]


        print(network_info)

        network = {
            "id" : network_info[0],
            "gateway_mac" : network_info[1],
            "name" : network_info[2],
            "ssid" : network_info[3]} 

        # { mac : Device }
        devices_info = {}

        # Converts all responses into Device objects
        for response in devices:
            new_device = Device(response[0], response[1])
            new_device.mac_vendor = response[2]
            new_device.hostname = response[3]
            new_device.os_type = response[4]
            new_device.os_vendor = response[5]
            new_device.os_family = response[6]
            new_device.parent = response[7]
            print(response[8])

            devices_info[response[1]] = new_device.to_json()

        network["devices"] = devices_info

        return network


    # Allows users to rename a network and all its data
    def rename_network(self, network_id, new_name):

        if not self.contains_network(network_id):
            return False

        query = """
                UPDATE networks
                SET name = ?
                WHERE id = ?;
                """

        params = (network_id, old_name,)

        self.query(query, params)
        return True


    # Adds a device into the database
    def add_device(self, network_id, device, ts):

        query = """
                INSERT INTO devices(mac, ip, mac_vendor, hostname, os_type, os_vendor, os_family, parent, network_id, timestamp)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """

        params = (device.mac, device.ip, device.mac_vendor, device.hostname, device.os_type,
                 device.os_vendor, device.os_family, device.parent, network_id, ts,)

        self.query(query, params)


    # Checks if a device is in the database. Devices are stored by MAC address, and thus we check if the db contains the MAC.
    def contains_mac(self, network_id, mac, ts):
        
        query = """
                SELECT 1
                FROM devices 
                WHERE mac = ? AND network_id = ? AND timestamp = ?;
                """

        params = (mac, network_id, ts,)

        response = self.query(query, params, res=True)
        return response != None and len(response) > 0 != None

    def get_most_recent_ts(self, network_id):
        
        query = """
                SELECT DISTINCT timestamp
                FROM devices
                WHERE network_id = ?;
                """

        params = (network_id,)

        response = self.query(query, params, res=True)

        if response == None or len(response) == 0:
            return None

        max = datetime.fromtimestamp(response[0][0])
        for resp in response:
            dt = datetime.fromtimestamp(resp[0])
            max = max if max > dt else dt

        print(response)
        return max


    # Gets all devices stored in the network corresponding to the gateway's MAC address
    def get_all_devices(self, network_id, ts=None):

        if ts == None:
            ts = self.get_most_recent_ts(network_id)

        query = """
                SELECT ip, mac, mac_vendor, hostname, os_type, os_vendor, os_family, parent
                FROM devices
                WHERE network_id = ? AND timestamp = ?;
                """

        params = (network_id, ts,)

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

            devices[response[1]] = new_device

        return devices


    # Retrieves a device from the database by a combination of it's MAC address and the gateway's MAC address
    def get_device(self, network_id, mac, ts):

        query = """
                SELECT ip, mac, mac_vendor, hostname, os_type, os_vendor, os_family, parent
                FROM devices
                WHERE network_id = ? AND mac = ? AND timestamp = ?;
                """
            
        params = (network_id, mac, ts,)

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
    def save_device(self, network_id, device, ts):

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
                WHERE network_id = ? AND mac = ? AND timestamp = ?;
                """

        params = (device.mac, device.ip, device.mac_vendor,
                  device.hostname, device.os_type, device.os_vendor,
                  device.os_family, device.parent, network_id, device.mac, ts,)

        self.query(query, params)


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
                            (id INTEGER PRIMARY KEY,
                            gateway_mac TEXT,
                            name TEXT,
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
                            network_id TEXT REFERENCES networks (id),
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
        # self.query(query_layer3s)
        # self.query(query_wirelessaps)
        self.query(query_alive)
        # self.query(query_layer3_ports)

        return True
