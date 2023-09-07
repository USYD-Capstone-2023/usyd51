#!/usr/bin/python
import psycopg2

from device import Device


class PostgreSQLDatabase:

    def __init__(self, database, username, password, host="localhost", port="5432"):
        self.connection = None
        self.cursor = None

        self.db = database
        self.un = username
        self.ps = password

        self.host = host
        self.port = port

        self.init_db()
        self.init_tables()


    def init_db(self):

        conn = None
        try:
            ## Open Database Connection
            conn = psycopg2.connect(
                user=self.un,
                password=self.ps,
                host=self.host,
                port=self.port,
            )

            conn.autocommit = True

            # Create Cursor Object
            cur = conn.cursor()

            # Checks if the database exists, creates a new one if not
            cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = '%s';" % (self.db))
            db_exists = cur.fetchone()
            if not db_exists:

                print("[INFO] Creating database...")
                cur.execute("CREATE DATABASE %s;" % (self.db))
                conn.commit()
                
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            if conn:
                cur.close()
                conn.close()

    def query(self, querystring, res=False):

        response = None
        conn = None
        try:
            ## Open Database Connection
            conn = psycopg2.connect(
                user=self.un,
                password=self.ps,
                host=self.host,
                port=self.port,
                database=self.db,
            )

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

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            print(querystring)

        finally:
            if conn:
                cur.close()
                conn.close()

        return response

    
    # Adds a network to the database if it doesnt already exist.
    def register_network(self, gateway_mac, ssid, name):

        print(f"{name} {ssid} {gateway_mac}")

        if not self.contains_network(gateway_mac):

            print("[INFO] Registering new network...")

            q = """INSERT INTO networks (gateway_mac, ssid, name)
                VALUES ('%s', '%s', '%s');
                """ % (gateway_mac, ssid, name)
            
            self.query(q)

    
    # Deletes a network from the database
    def delete_network(self, gateway_mac):

        if not self.contains_network(gateway_mac):
            return False

        q = """DELETE FROM networks
               WHERE gateway_mac = '%s';

               DELETE FROM devices
               WHERE gateway_mac = '%s';
            """ % (gateway_mac, gateway_mac)

        self.query(q) 
        return True


    # Checks if the current network exists in the database
    def contains_network(self, gateway_mac):

        q = """SELECT 1
               FROM networks
               WHERE gateway_mac = '%s';
            """ % (gateway_mac)
        
        response = self.query(q, res=True)

        return response != None and len(response) > 0

    
    def get_network_names(self):

        q = """SELECT *
               FROM networks
            """

        response = self.query(q, res=True)

        return [{"mac" : x[0], "name" : x[1], "ssid" : x[2]} for x in response]
    
    
    def get_network(self, network_name):

        q = """SELECT ip, mac, mac_vendor, hostname, os_type, os_vendor, os_family, parent
               FROM devices JOIN networks ON  devices.gateway_mac = networks.gateway_mac
               WHERE networks.name = '%s';
            """ % (network_name)
        
        responses = self.query(q, res=True)

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



    # Adds a device into the database
    def add_device(self, gateway_mac, device):

        q = """INSERT INTO devices(mac, ip, mac_vendor, hostname, os_type, os_vendor, os_family, parent, gateway_mac)
               VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
            """ % (device.mac, device.ip, device.mac_vendor, device.hostname, device.os_type, device.os_vendor, device.os_family, device.parent, gateway_mac)
        
        self.query(q)


    # Checks if a device is in the database. Devices are stored by MAC address, and thus we check if the db contains the MAC.
    def contains_mac(self, gateway_mac, mac):

        q = """SELECT 1
               FROM devices 
               WHERE mac='%s' AND gateway_mac='%s';
            """ % (mac, gateway_mac)
        
        response = self.query(q, res=True)
        return len(response) > 0
        

    # Gets all devices stored in the network corresponding to the gateway's MAC address
    def get_all_devices(self, gateway_mac):

        q = """SELECT ip, mac, mac_vendor, hostname, os_type, os_vendor, os_family, parent
               FROM devices
               WHERE gateway_mac='%s';
            """ % (gateway_mac)
        
        responses = self.query(q, res=True)

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
    def get_device(self, gateway_mac, mac):

        q = """SELECT ip, mac, mac_vendor, hostname, os_type, os_vendor, os_family, parent
               FROM devices
               WHERE gateway_mac='%s' AND mac='%s';
            """ % (gateway_mac, mac)
        
        response = self.query(q, res=True)

        if len(response) == 0 or len(response[0]) < 8:
            print(response)
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
    def save_device(self, gateway_mac, device):

        q = """UPDATE devices
               SET mac = '%s',
                   ip = '%s',
                   mac_vendor = '%s',
                   hostname = '%s',
                   os_type = '%s',
                   os_vendor = '%s',
                   os_family = '%s',
                   parent = '%s'
               WHERE gateway_mac='%s' AND mac='%s';
            """ % (device.mac, device.ip, device.mac_vendor, device.hostname, device.os_type, device.os_vendor, device.os_family, device.parent, gateway_mac, device.mac)
        
        self.query(q)

    
    def clear(self):

        q = """DROP DATABASE %s""" % (self.db)

        self.query(q)

        self.init_db()



    # Setup tables if it doesn't exist
    # Currently using router MAC as PK for networks, need to find something much better
    def init_tables(self):
        # Main Tables
        # query_users = """CREATE TABLE IF NOT EXISTS users
        #                 (id TEXT PRIMARY KEY NOT NULL,
        #                 email TEXT NOT NULL,
        #                 password TEXT NOT NULL,
        #                 company TEXT NOT NULL);
        #                 """
        
        query_networks = """CREATE TABLE IF NOT EXISTS networks
                        (gateway_mac TEXT PRIMARY KEY NOT NULL,
                        name TEXT,
                        ssid TEXT);
                        """
        
        query_devices = """CREATE TABLE IF NOT EXISTS devices
                        (mac TEXT NOT NULL,
                        ip TEXT NOT NULL,
                        mac_vendor TEXT,
                        hostname TEXT,
                        os_type TEXT,
                        os_vendor TEXT,
                        os_family TEXT,
                        parent TEXT,
                        gateway_mac TEXT REFERENCES networks (gateway_mac) ON DELETE CASCADE,
                        CONSTRAINT id PRIMARY KEY (mac, gateway_mac));
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
        query_alive = """CREATE TABLE IF NOT EXISTS alive
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

        
