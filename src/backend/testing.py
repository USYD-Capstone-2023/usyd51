import unittest
import socket

from database import PostgreSQL_database

VALID_NETWORK_KEYS = ["id", "ssid", "gateway_mac", "name"]
VALID_NETWORK_VALUES = ["1", "test_network_ssid", "12:34:56:78:90:AB", "test_network_name"]
VALID_DEVICE_KEYS = ["mac", "ip", "mac_vendor", "os_family", "os_vendor", "os_type", "hostname", "parent", "ports"]
VALID_DEVICE_VALUES = ["FE:DC:BA:09:87:65", "198.162.0.1", "test_vendor", "test_os", "test_os_vendor", "test_os_type", "test_host", "test_parent", "22,80,500"]

def get_ip_address():
    # Create a socket object to get the local hostname
    hostname = socket.gethostname()
    # Get the IP address associated with the local hostname
    ip_address = socket.gethostbyname(hostname)
    return ip_address

class DatabaseTester(unittest.Testcase):


    # template for copy pasting purpose
    """
    Tests 
    Preconditions:
    Postconditions:
    """
    def test_(self):
        pass

    # before each
    def setUp(self):
        self.postgres = PostgreSQL_database("testing_database", "user", "password")
        
        # TODO
        # some dummy data to test queries

        # just need a different ID to test anything that is register
        network_vals = ["0", "test_network_ssid", "12:34:56:78:90:AB", "test_network_name"]
        test_network = dict(zip(VALID_DEVICE_KEYS, network_vals))
        self.postgres.register_network(test_network)

    # after each
    def tearDown(self):
        pass

    def test_query(self):
        pass

    """
    Tests register_network with positive inputs
    Preconditions: PostgeSQL database exists
    Postconditions: Network successfully registered and added to the database
    """
    def test_net_reg_pos(self):
        network = dict(zip(VALID_NETWORK_KEYS, VALID_NETWORK_VALUES))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("1")
        db_network = self.postgres.get_network("1")

        self.assertTrue(reg_result)
        self.assertTrue(contain_result)
        self.assertEquals(network, db_network)

    """
    Tests register_network with extra keys and values in the network
    Preconditions: PostgeSQL database exists
    Postconditions: 
    """
    def test_net_reg_pos_extra_key_vals(self):
        network_keys = VALID_NETWORK_KEYS + ["some", "dummy", "keys"]
        network_vals = VALID_NETWORK_VALUES + ["some", "dummy", "values"]
        network = dict(zip(network_keys, network_vals))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("1")
        db_network = self.postgres.get_network("1")

        self.assertTrue(reg_result)
        self.assertTrue(contain_result)
        self.assertIsNotNone(db_network)

    """
    Tests register_network with bad network keys
    Preconditions: PostgeSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_net_reg_neg_bad_keys(self):
        network_keys = VALID_NETWORK_KEYS[:] # copy valid keys
        network_keys[2] = "bad_key"
        network = dict(zip(network_keys, VALID_NETWORK_VALUES))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("1")
        db_network = self.postgres.get_network("1")

        self.assertFalse(reg_result)
        self.assertFalse(contain_result)
        self.assertIsNone(db_network)

    """
    Tests register_network with a bad network id
    Preconditions: PostgeSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_net_reg_neg_bad_id(self):
        network_vals = ["bad", "test_network", "12:34:56:78:90:AB", "test_network"]
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("1")
        db_network = self.postgres.get_network("1")

        self.assertFalse(reg_result)
        self.assertFalse(contain_result)
        self.assertIsNone(db_network)


    """
    Tests register_network with a malformed mac address
    Preconditions: PostgeSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_net_reg_neg_bad_mac(self):
        network_vals = VALID_NETWORK_VALUES[:] # copy valid values
        network_vals[2] = "GG:PP:gg:oo:..:()"
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("1")
        db_network = self.postgres.get_network("1")

        self.assertFalse(reg_result)
        self.assertFalse(contain_result)
        self.assertIsNone(db_network)
        
    """
    Tests register_network for sql injection
    Preconditions: PostgeSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_net_reg_neg_sql_inj(self):
        # This currently assumes ";DROP TABLE networks;" is an invalid name
        # If it should be a valid name, and we allow ; in names, change this test case
        network_vals = VALID_NETWORK_VALUES[:] # copy valid values
        network_vals[1] = ";DROP TABLE networks;"
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("1")
        db_network = self.postgres.get_network("1")
        tables = self.postgres.db.query("""SHOW TABLES""")

        # tables should be a list of tuples containing aliases
        passed_sql = False
        for table in tables:
            if "networks" in table:
                passed_sql = True
                break
        
        self.assertTrue(passed_sql)
        self.assertFalse(reg_result)
        self.assertFalse(contain_result)
        self.assertIsNone(db_network)

    """
    Tests register_network with empty input
    Preconditions: PostgeSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_net_reg_neg_empty(self):
        network = dict(zip([], []))

        reg_result = self.postgres.register_network(network)
        
        self.assertFalse(reg_result)

    """
    Tests save_devices with positive input
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database successfully added the device to the network
                    and the network contains the device
    """
    def test_save_devices_pos(self):
        device = dict(zip(VALID_DEVICE_KEYS, VALID_DEVICE_VALUES))

        # save_devices uses devices as a dictionary for some reason? not sure
        # why its not a list, as the keys are never used but whatever
        devices = {0: device}

        save_result = self.postgres.save_devices("0", devices, 0)
        contains_result = self.postgres.contains_mac(0, device["mac"], 0)
        device_result = self.postgres.get_all_devices(0,0)
        
        self.assertTrue(save_result)
        self.assertTrue(contains_result)
        self.assertEqual(len(device_result), 1)

    """
    Tests save_devices with positive input, with lower case MAC address
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database successfully added the device to the network
                    and the network contains the device
    """
    def test_save_devices_pos_case_sens_mac(self):
        device_vals = VALID_DEVICE_VALUES[:] # copy valid values
        device_vals[0] = "ab:CD:ef:12:34:56"
        device = dict(zip(VALID_DEVICE_KEYS, device_vals))

        save_result = self.postgres.save_devices("0", {0:device}, 0)
        contains_result = self.postgres.contains_mac(0, device["mac"], 0)
        device_result = self.postgres.get_all_devices(0,0)
        
        self.assertTrue(save_result)
        self.assertTrue(contains_result)
        self.assertEqual(len(device_result), 1)

    """
    Tests save_devices with bad keys
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database does not add the device to the network
    """
    def test_save_devices_neg_bad_keys(self):
        device_keys = VALID_DEVICE_KEYS[:] # copy valid values
        device_keys[1] = "bad"
        device = dict(zip(device_keys, VALID_DEVICE_VALUES))

        save_result = self.postgres.save_devices(0,{0:device},"0")
        contains_result = self.postgres.contains_mac("0",device["mac"],0)
        device_result = self.postgres.get_all_devices(0,0)

        self.assertFalse(save_result)
        self.assertFalse(contains_result)
        self.assertEquals(len(device_result), 0)

    """
    Tests save_devices with a bad MAC address
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database does not add the device to the network
    """
    def test_save_devices_neg_bad_mac_1(self):
        device_vals = VALID_DEVICE_VALUES[:] # copy valid values
        device = dict(zip(VALID_DEVICE_KEYS, device_vals))

        bad_macs = [
            "FG:QW:ZR:ET:XA:==",        # bad chars
            "1234567890ABCDEFabcdef",   # no :
            "123:abc:fff:ee:00:11",     # too many chars
            "1:A:0:AA:BB:CC",           # too few chars
            ":::::",                    # too few chars
        ]

        for bad_mac in bad_macs:

            device["mac"] = bad_mac

            save_result = self.postgres.save_devices(0,{0:device},"0")
            contains_result = self.postgres.contains_mac("0",device["mac"],0)
            device_result = self.postgres.get_all_devices(0,0)

            self.assertFalse(save_result)
            self.assertFalse(contains_result)
            self.assertEquals(len(device_result), 0)

    """
    Tests save_devices with a bad IP addresses
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database does not add the device to the network
    """
    def test_save_devices_neg_bad_ips(self):
        device_vals = VALID_DEVICE_VALUES[:] # copy valid values

        device = dict(zip(VALID_DEVICE_KEYS, device_vals))

        bad_ips = [
            "a.2.b.c",          # bad chars
            "127001",           # no .
            "999.990.900.69",   # out of range
            "0123.0000.042.069",# too many chars
            "...",              # too few chars
        ]

        for bad_ip in bad_ips:

            device["ip"] = bad_ip

            save_result = self.postgres.save_devices(0,{0:device},"0")
            contains_result = self.postgres.contains_mac("0",device["mac"],0)
            device_result = self.postgres.get_all_devices(0,0)

            self.assertFalse(save_result)
            self.assertFalse(contains_result)
            self.assertEquals(len(device_result), 0)

    # this could be changed to a positive test case
    # we should consider expected behaviour for this though
    """
    Tests save_devices with zero devices
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database does not add the device to the network
    """
    def test_save_devices_neg_empty(self):
        save_result = self.postgres.save_devices(0,{},0)
        device_result = self.postgres.get_all_devices(0,0)

        self.assertFalse(save_result)
        self.assertEquals(len(device_result),0)

    """
    Tests save_devices with SQL injection
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database does not add the device to the network
    """
    def test_save_devices_neg_sql_inj(self):
        device_vals = VALID_DEVICE_VALUES[:] # copy valid values
        device_vals[0] = ";DROP TABLE networks;"
        device = dict(zip(VALID_DEVICE_KEYS, device_vals))

        save_result = self.postgres.save_devices(0,{0:device},0)
        device_result = self.postgres.get_all_devices(0,0)
        tables = self.postgres.db.query("""SHOW TABLES""")

        # tables should be a list of tuples containing aliases
        passed_sql = False
        for table in tables:
            if "networks" in table:
                passed_sql = True
                break
        
        self.assertTrue(passed_sql)
        self.assertFalse(save_result)
        self.assertEquals(len(device_result),0)

    """
    Tests delete_network with positive input
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database deletes the network successfully
    """
    def test_delete_network_pos(self):
        del_result = self.postgres.delete_network("0")
        network_result = self.postgres.get_network("0")
        networks_result = self.postgres.get_networks()

        self.assertTrue(del_result)
        self.assertIsNone(network_result)
        self.assertEquals(len(networks_result), 0)

    """
    Tests delete_network with a non-existent network
    Preconditions: PostgreSQL database exists
    Postconditions: The database does nothing
    """
    def test_delete_network_neg_bad_network(self):
        del_result = self.postgres.delete_network("1")
        networks_result = self.postgres.get_networks()

        self.assertFalse(del_result)
        self.assertEquals(len(networks_result), 1)

    """
    Tests delete_network with SQL injection
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database does not delete the network
                    and does not allow SQL injection
    """
    def test_delete_network_neg_sql_inj(self):
        del_result = self.postgres.delete_network(";DROP TABLE networks;")
        network_result = self.postgres.get_network("0")
        networks_result = self.postgres.get_networks()
        tables = self.postgres.db.query("""SHOW TABLES""")

        # tables should be a list of tuples containing aliases
        passed_sql = False
        for table in tables:
            if "networks" in table:
                passed_sql = True
                break
        
        self.assertTrue(passed_sql)
        self.assertFalse(del_result)
        self.assertIsNotNone(network_result)
        self.assertEquals(len(networks_result), 1)
    
    def test_contains_network_pos(self):
        pass
    
    def test_contains_network_neg(self):
        pass

    def test_get_networks(self):
        pass

    def test_get_network_pos(self):
        pass
    
    def test_get_network_neg(self):
        pass

    def test_rename_network_pos(self):
        pass

    def test_rename_network_neg(self):
        pass

    def test_add_device(self):
        pass
    
    def test_udpate_device(self):
        pass

    def test_contains_mac_pos(self):
        pass

    def test_contains_mac_neg(self):
        pass

    def test_get_most_recent_ts_pos(self):
        pass

    def test_get_most_recent_ts_neg(self):
        pass

    def test_get_all_devices(self):
        pass
    
    def test_get_next_network_id(self):
        pass
    

                

if __name__ == '__main__':
    unittest.main()