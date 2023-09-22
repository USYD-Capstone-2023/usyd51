import unittest
import socket

from database import PostgreSQL_database

VALID_NETWORK_KEYS = ["id", "ssid", "gateway_mac", "name"]

def get_ip_address():
    # Create a socket object to get the local hostname
    hostname = socket.gethostname()
    # Get the IP address associated with the local hostname
    ip_address = socket.gethostbyname(hostname)
    return ip_address

class DatabaseTester(unittest.Testcase):

    # before each
    def setUp(self):
        self.postgres = PostgreSQL_database("testing_database", "user", "password")
        
        # TODO
        # some dummy data to test queries

    # after each
    def tearDown(self):
        pass

    def test_query(self):
        pass

    """
    Tests network registration with positive inputs
    Preconditions:  PostgeSQL database exists
    Postconditions: Network successfully registered and added to the database
    """
    def test_net_reg_pos(self):
        network_vals = ["1", "test_network", "12:34:56:78:90:AB", "test_network"]
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("1")
        db_network = self.postgres.get_network("1")

        self.assertTrue(reg_result)
        self.assertTrue(contain_result)
        self.assertEquals(network, db_network)

    """

    """
    def test_net_reg_neg_bad_keys(self):
        network_keys = ["id", "ssid", "bad_key", "name"]
        network_vals = ["1", "test_network", "12:34:56:78:90:AB", "test_network"]
        network = dict(zip(network_keys, network_vals))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("1")
        db_network = self.postgres.get_network("1")

        self.assertFalse(reg_result)
        self.assertFalse(contain_result)
        self.assertIsNone(db_network)

    """

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

    """
    def test_net_reg_neg_bad_mac(self):
        network_vals = ["1", "test_network", "GG:PP:gg:oo:..:()", "test_network"]
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("1")
        db_network = self.postgres.get_network("1")

        self.assertFalse(reg_result)
        self.assertFalse(contain_result)
        self.assertIsNone(db_network)

        
    """

    """
    def test_net_reg_neg_sql_inj(self):
        # This currently assumes ";DROP TABLE networks;" is an invalid name
        # If it should be a valid name, and we allow ;'s in names, change this test case
        network_vals = ["1", ";DROP TABLE networks;", "12:34:56:78:90:AB", "test_network"]
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("1")
        db_network = self.postgres.get_network("1")
        tables = self.postgres.db.query("""SHOW TABLES""")

        # tables should be a list tuples containing aliases
        passed = False
        for table in tables:
            if "networks" in table:
                passed = True
                break
        
        self.assertTrue(passed)
        self.assertFalse(reg_result)
        self.assertFalse(contain_result)
        self.assertIsNone(db_network)
        

    def test_save_devices_pos(self):
        pass
    
    def test_save_devices_neg(self):
        pass
    
    def test_delete_network_pos(self):
        pass

    def test_delete_network_neg(self):
        pass
    
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