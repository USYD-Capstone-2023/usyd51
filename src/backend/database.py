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
                # print(response)
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
                # print("PostgreSQL connection is closed")

        return response

    def add_device(self, device, network_id):

        q = """INSERT INTO devices(mac, ip, mac_vendor, hostname, os_type, os_vendor, os_family, network_id)
               VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
            """ % (device.mac, device.ip, device.mac_vendor, device.hostname, device.os_type, device.os_vendor, device.os_family, network_id)
        
        self.query(q)


    def contains_mac(self, mac, network_id):

        q = """SELECT 1
               FROM devices 
               WHERE mac='%s' AND network_id='%s';
            """ % (mac, network_id)
        
        result = self.query(q, res=True)
        return len(result) > 0
    

    def register_network(self, network_id, network_name):

        q = """SELECT 1
               FROM networks
               WHERE router_mac='%s';
            """ % (network_id)
        
        result = self.query(q, res=True)

        if len(result) == 0:

            print("[INFO] Registering new network...")

            q = """INSERT INTO networks (router_mac, name)
                VALUES ('%s', '%s');
                """ % (network_id, network_name)
            
            self.query(q)
        

    def get_all_devices(self, gateway_mac):

        q = """SELECT ip, mac, mac_vendor, hostname, os_type, os_vendor, os_family
               FROM devices
               WHERE network_id='%s';
            """ % (gateway_mac)
        
        responses = self.query(q, res=True)

        # { mac : Device }
        devices = {}
        for response in responses:
            
            new_device = Device(response[0], response[1])
            new_device.mac_vendor = response[2]
            new_device.hostname = response[3]
            new_device.os_type = response[4]
            new_device.os_vendor = response[5]
            new_device.os_family = response[6]

            devices[response[0]] = new_device

        return devices


    def get_device(self, network_id, mac):

        q = """SELECT mac, ip, mac_vendor, hostname, os_type, os_vendor, os_family
               FROM devices
               WHERE network_id='%s' AND mac='%s';
            """ % (network_id, mac)
        
        response = self.query(q, res=True)

        new_device = Device(response[0], response[1])
        new_device.mac_vendor = response[2]
        new_device.hostname = response[3]
        new_device.os_type = response[4]
        new_device.os_vendor = response[5]
        new_device.os_family = response[6]

        return new_device


    def save_device(self, device, network_id):

        q = """UPDATE devices
               SET mac = '%s',
                   ip = '%s',
                   mac_vendor = '%s',
                   hostname = '%s',
                   os_type = '%s',
                   os_vendor = '%s',
                   os_family = '%s'
               WHERE network_id='%s' AND mac='%s';
            """ % (device.mac, device.ip, device.mac_vendor, device.hostname, device.os_type, device.os_vendor, device.os_family, network_id, device.mac)
        
        self.query(q)


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
                        (router_mac TEXT PRIMARY KEY NOT NULL,
                        name TEXT);
                        """
        
        query_devices = """CREATE TABLE IF NOT EXISTS devices
                        (mac TEXT PRIMARY KEY,
                        ip TEXT NOT NULL,
                        mac_vendor TEXT,
                        hostname TEXT,
                        os_type TEXT,
                        os_vendor TEXT,
                        os_family TEXT,
                        network_id TEXT REFERENCES networks (router_mac));
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

        
