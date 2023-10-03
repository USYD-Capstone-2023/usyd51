import unittest

from database import PostgreSQL_database

VALID_NETWORK_KEYS = ["network_id", "ssid", "gateway_mac", "name", "devices", "timestamp"]
VALID_NETWORK_VALUES = [1, "test_network_ssid", "12:34:56:78:90:AB", "test_network_name", {}, 0]
VALID_DEVICE_KEYS = ["mac", "ip", "mac_vendor", "os_family", "os_vendor", "os_type", "hostname", "parent", "ports"]
VALID_DEVICE_VALUES = ["FE:DC:BA:09:87:65", "198.162.0.1", "test_vendor", "test_os", "test_os_vendor", "test_os_type", "test_host", "test_parent", "22,80,500"]

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

        self.postgres.register_network(self.get_test_network())

    # after each
    def tearDown(self):
        self.postgres = None

    # checks my common sql injection phrase
    # returns True if the SQL injection does not work, False otherwise
    # i.e. we want this to be returning True
    def check_sql_tables(self, name="networks") -> bool:
        tables = self.postgres.query("""SHOW TABLES""")

        # tables should be a list of tuples containing aliases
        passed_sql = False
        for table in tables:
            if name in table:
                passed_sql = True
                break
        
        return passed_sql
    
    # returns a test network to remain consistent
    def get_test_network(self) -> dict:
        network_vals = VALID_NETWORK_VALUES[:] # copy valid values
        network_vals[0] = 0
        return dict(zip(VALID_DEVICE_KEYS, network_vals))
        

    """
    Tests save_network with positive inputs
    Preconditions: PostgeSQL database exists
    Postconditions: Network successfully registered and added to the database
    """
    def test_save_net_pos(self):
        network = dict(zip(VALID_NETWORK_KEYS, VALID_NETWORK_VALUES))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("1")
        db_network = self.postgres.get_network("1")

        self.assertTrue(reg_result)
        self.assertTrue(contain_result)
        self.assertEqual(network, db_network)

    """
    Tests save_network with extra keys and values in the network
    Preconditions: PostgeSQL database exists
    Postconditions: 
    """
    def test_save_net_pos_extra_key_vals(self):
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
    Tests save_network with bad network keys
    Preconditions: PostgeSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_neg_bad_keys(self):
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
    Tests save_network with a network id of chars
    Preconditions: PostgeSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_neg_bad_id_chars(self):
        network_vals = ["bad", "test_network", "12:34:56:78:90:AB", "test_network"]
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("1")
        db_network = self.postgres.get_network("1")

        self.assertFalse(reg_result)
        self.assertFalse(contain_result)
        self.assertIsNone(db_network)

    """
    Tests save_network with a network id < 0
    Preconditions: PostgeSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_neg_bad_id(self):
        network_vals = ["-1", "test_network", "12:34:56:78:90:AB", "test_network"]
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("-1")
        db_network = self.postgres.get_network("-1")

        self.assertFalse(reg_result)
        self.assertFalse(contain_result)
        self.assertIsNone(db_network)


    """
    Tests save_network with a malformed mac address
    Preconditions: PostgeSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_neg_bad_mac(self):
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
    Tests save_network for sql injection
    Preconditions: PostgeSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_neg_sql_inj(self):
        # This currently assumes ";DROP TABLE networks;" is an invalid name
        # If it should be a valid name, and we allow ; in names, change this test case
        network_vals = VALID_NETWORK_VALUES[:] # copy valid values
        network_vals[1] = ";DROP TABLE networks;"
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        reg_result = self.postgres.register_network(network)
        contain_result = self.postgres.contains_network("1")
        db_network = self.postgres.get_network("1")
        
        self.assertTrue(self.check_sql_tables())
        self.assertFalse(reg_result)
        self.assertFalse(contain_result)
        self.assertIsNone(db_network)

    """
    Tests save_network with empty input
    Preconditions: PostgeSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_neg_empty(self):
        network = dict(zip([], []))

        reg_result = self.postgres.register_network(network)
        
        self.assertFalse(reg_result)

    """
    Tests save_network with a duplicate ID
    Preconditions: PostgeSQL database exists, network 0 exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_neg_duplicate_id(self):
        network = self.get_test_network()

        reg_result = self.postgres.register_network(network)
        
        self.assertFalse(reg_result)

    """
    Tests save_network with empty input
    Preconditions: PostgeSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_neg_duplicate_id(self):
        network_vals = VALID_NETWORK_VALUES
        network_vals[0] = "0"
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

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
    
    # not too sure if post conditions here are correct, but as it stands,
    # this is what the test case expects, change if functionality should be
    # different
    """
    Tests save_devices with multiple devices, some malformed (values), some good
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database successfully adds well formed devices
                    and doesn't add the malformed ones
    """
    def test_save_devices_pos_bad_device_vals(self):

        device_vals = VALID_DEVICE_VALUES[:] # copy valid values

        device_macs = [
            "FE:DC:BA:09:87:65",    # valid macs
            "FE:DC:BA:09:87:66",
            "FE:DC:BA:09:87:67",
            "-----------------",    # bad mac
            "FE:DC:BA:09:87:68",    # valid mac
            "-----------------",    # bad mac
            "FE:DC:BA:09:87:69",    # valid mac
        ]

        devices = {}

        for i, mac in enumerate(device_macs):
            device_vals[0] = mac
            device = dict(zip(VALID_DEVICE_KEYS, device_vals))

            devices[i] = device
        
        save_result = self.postgres.save_devices(0, devices, 0)

        # results of contains check for all devices
        contains_results = [self.postgres.contains_mac(0, device["mac"], 0) for device in devices]
        devices_result = self.postgres.get_all_devices(0,0)

        self.assertTrue(save_result)
        for i, result in enumerate(contains_results):
            if i in (3,5):
                self.assertFalse(result)
            else:
                self.assertTrue(result)
        self.assertEqual(len(devices_result), 5)

    # once again, as above, post conditions could be wrong,
    # change if necessary
    """
    Tests save_devices with multiple devices, some malformed (keys), some good
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database successfully adds well formed devices
                    and doesn't add the malformed ones
    """
    def test_save_devices_pos_one_bad_device_keys(self):
        device_keys = VALID_DEVICE_KEYS[:] # copy valid keys
        device_vals = VALID_DEVICE_VALUES[:] # copy valid values

        device_macs = [
            "FE:DC:BA:09:87:65",
            "FE:DC:BA:09:87:66",
            "FE:DC:BA:09:87:67",
            "FE:DC:BA:09:87:68",
            "FE:DC:BA:09:87:69",
        ]

        devices = {}

        for i, mac in enumerate(device_macs):
            if i in (1,3):
                device_keys[0] = "bad_key"
            device_vals[0] = mac
            device = dict(zip(device_keys, device_vals))

            devices[i] = device

        save_result = self.postgres.save_devices(0, devices, 0)

        # results of contains check for all devices
        contains_results = [self.postgres.contains_mac(0, device["mac"], 0) for device in devices]
        devices_result = self.postgres.get_all_devices(0,0)

        self.assertTrue(save_result)
        for i, result in enumerate(contains_results):
            if i in (1,3):
                self.assertFalse(result)
            else:
                self.assertTrue(result)
        self.assertEqual(len(devices_result), 3)

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
        self.assertEqual(len(device_result), 0)

    """
    Tests save_devices with a bad MAC addresses
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
            self.assertEqual(len(device_result), 0)

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
            self.assertEqual(len(device_result), 0)

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
        self.assertEqual(len(device_result),0)

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
        
        self.assertTrue(self.check_sql_tables())
        self.assertFalse(save_result)
        self.assertEqual(len(device_result),0)

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
        self.assertEqual(len(networks_result), 0)

    """
    Tests delete_network with a non-existent network
    Preconditions: PostgreSQL database exists
    Postconditions: The database does nothing
    """
    def test_delete_network_neg_bad_network(self):
        del_result = self.postgres.delete_network("1")
        networks_result = self.postgres.get_networks()

        self.assertFalse(del_result)
        self.assertEqual(len(networks_result), 1)

    """
    Tests delete_network with SQL injection
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database does not delete the network
                    and does not allow SQL injection
    """
    def test_delete_network_neg_sql_inj(self):
        del_result = self.postgres.delete_network(";DROP TABLE networks;")
        networks_result = self.postgres.get_networks()

        self.assertTrue(self.check_sql_tables())
        self.assertFalse(del_result)
        self.assertEqual(len(networks_result), 1)
    
    """
    Tests contains_network with positive input
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: contains_network is true, nothing changes in database
    """
    def test_contains_network_pos(self):
        contains_result = self.postgres.contains_network(0)
        network_result = self.postgres.get_network(0)

        test_network = self.get_test_network()

        self.assertTrue(contains_result)
        self.assertEqual(network_result, test_network)
    
    """
    Tests contains_network with non-existent network
    Preconditions: PostgreSQL database exists
    Postconditions: contains_network is false
    """
    def test_contains_network_neg_bad_network(self):
        contains_result = self.postgres.contains_network(1)

        self.assertFalse(contains_result)

    """
    Tests contains_network with SQL injection
    Preconditions: PostgreSQL database exists
    Postconditions: contains_network is false, nothing changes in database
    """
    def test_contains_network_neg_sql_inj(self):
        contains_result = self.postgres.contains_network(";DROP TABLE networks;")
        
        self.assertTrue(self.check_sql_tables())
        self.assertFalse(contains_result)

    """
    Tests get_networks with one network
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: get_networks contains only newtork 0
    """
    def test_get_networks_pos(self):
        networks_result = self.postgres.get_networks()

        test_network = self.get_test_network()

        self.assertTrue(test_network in networks_result)
        self.assertEqual(len(networks_result), 1)

    """
    Tests get_networks with no networks
    Preconditions: PostgreSQL database exists,
                   networks table is empty - satisfied in this test
    Postconditions: get_networks returns an empty list
    """
    def test_get_networks_pos(self):
        self.postgres.delete_network(0)
        networks_result = self.postgres.get_networks()

        self.assertEqual(len(networks_result), 0)

    """
    Tests get_network with an existing network
    Preconditions: PostgreSQL database exits, network 0 exists
    Postconditions: get_network returns the correct network
    """
    def test_get_network_pos(self):
        network_result = self.postgres.get_network(0)

        test_network = self.get_test_network()

        self.assertEqual(network_result, test_network)
    
    # unsure if postconditions are correct, change if needed
    """
    Tests get_network with a network that isn't in the database
    Preconditions: PostgreSQL database exists
    Postconditions: get_network returns None
    """
    def test_get_network_neg_bad_network(self):
        network_result = self.postgres.get_network(1)

        self.assertIsNone(network_result)

    # unsure if postconditions are correct, change if needed
    """
    Tests get_network for SQL injection
    Preconditions: PostgreSQL database exists
    Postconditions: get_network returns None, and SQL injection fails
    """
    def test_get_network_neg_sql_inj(self):
        network_result = self.postgres.get_network("; DROP TABLE networks;")
        
        self.assertTrue(self.check_sql_tables())
        self.assertIsNone(network_result)

    """
    Tests rename_network with positive input
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: rename_networks returns true, and successfully renames the network
    """
    def test_rename_network_pos(self):
        rename_result = self.postgres.rename_network(0,"different_name")
        network_result = self.postgres.get_network(0)

        # test network with different name
        network_vals = VALID_NETWORK_VALUES[:] # copy valid values
        network_vals[0] = "0"
        network_vals[1] = "different_name"
        test_network = dict(zip(VALID_DEVICE_KEYS, network_vals))

        self.assertTrue(rename_result)
        self.assertEqual(network_result, test_network)

    """
    Tests rename_network on a non existent network
    Preconditions: PostgreSQL database exists
    Postconditions: rename_networks returns false, and does not rename any networks
    """
    def test_rename_network_neg_no_network(self):
        rename_result = self.postgres.rename_network(1, "different_name")
        network_result = self.postgres.get_network(0)

        self.assertFalse(rename_result)
        self.assertEqual(network_result, self.get_test_network())

    """
    Tests rename_network for SQL injection
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: rename_network returns 0, doesn't rename the network,
                    and SQL injection fails
    """
    def test_rename_network_neg_sql_inj(self):
        rename_result = self.postgres.rename_network(0, "; DROP TABLE networks;")
        network_result = self.postgres.get_network(0)

        self.assertEqual(network_result, self.get_test_network())
        self.assertTrue(self.check_sql_tables())
        self.assertFalse(rename_result)

    # this should totally be private and
    # is only used in a function that is already tested
    def test_add_device(self):
        pass
    
    # this isn't even used at all
    def test_udpate_device(self):
        pass

    # this should probably also be private I think
    # though, we likely should still test this one.
    def test_get_most_recent_ts_pos(self): pass
    def test_get_most_recent_ts_neg(self): pass

    """
    Tests get_all_devices with positive input
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: get_all_devices returns all of the correct devices
    """
    def test_get_all_devices_pos(self):
        device_keys = VALID_DEVICE_KEYS[:] # copy valid keys
        device_vals = VALID_DEVICE_VALUES[:] # copy valid values

        device_macs = [
            "FE:DC:BA:09:87:65",
            "FE:DC:BA:09:87:66",
            "FE:DC:BA:09:87:67",
            "FE:DC:BA:09:87:68",
            "FE:DC:BA:09:87:69",
        ]

        devices = []

        for i, mac in enumerate(device_macs):
            device_vals[0] = mac
            device = dict(zip(device_keys, device_vals))

            devices[i] = device

        save_result = self.postgres.save_devices(0, devices, 0)
        contains_results = [self.postgres.contains_mac(0, device["mac"], 0) for device in devices]
        devices_result = self.postgres.get_all_devices(0,0)

        self.assertTrue(save_result)
        for result in contains_results:
            self.assertTrue(result)
        self.assertEqual(len(devices_result), 5)

    """
    Tests get_all_devices with empty network
    Preconditions: PostgreSQL database exists, network 0 exists and is empty
    Postconditions: get_all_devices returns an empty list
    """
    def test_get_all_devices_pos_empty(self):
        devices_result = self.postgres.get_all_devices(0,0)

        self.assertEqual(devices_result, [])

    """
    Tests get_all_devices for SQL injection
    Preconditions: PostgreSQL datbase exists, network 0 exists
    Postconditions: get_all_devices returns an empty list and does not
                    allow SQL injection
    """
    def test_get_all_devices_neg_sql_inj(self):
        devices_result = self.postgres.get_all_devices("; DROP TABLE networks;")
        
        self.assertTrue(self.check_sql_tables())
        self.assertEqual(devices_result, [])

    # postcondition could be incorrect, change if needed
    """
    Tests get_all_devices on a non-existent network
    Preconditions: PostgreSQL datbase exists, network 1 does not exist
    Postconditions: get_all_devices returns an empty list
    """
    def test_get_all_devices_neg_no_network(self):
        devices_result = self.postgres.get_all_devices(1)

        self.assertEqual(devices_result, [])

    """
    Tests get_next_network_id with 1 network in the database.
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: get_next_network_id returns 1
    """
    def test_get_next_network_id_pos_one(self):
        next_result = self.postgres.get_next_network_id()

        self.assertEqual(next_result, 1)
    
    """
    Tests get_next_network_id with many networks in the database.
    Preconditions: PostgreSQL database exists and is populated
    Postconditions: get_next_network_id returns 69
    """
    def test_get_next_network_id_pos_many(self):
        new_ids = [68,30,21,19,7]

        networks = []

        for id in new_ids:
            vals = VALID_NETWORK_VALUES[:]
            vals[0] = id
            networks.append(dict(zip(VALID_NETWORK_KEYS, vals)))

        reg_results = [self.postgres.register_network(network) for network in networks]
        next_result = self.postgres.get_next_network_id()

        for result in reg_results:
            self.assertTrue(result)
        self.assertEqual(next_result, 69)

    """
    Tests get_next_network_id with no networks in the database.
    Preconditions: PostgreSQL database exists
    Postconditions: get_next_network_id returns 0
    """
    def test_get_next_network_id_pos_none(self):
        del_result = self.postgres.delete_network(0)
        next_result = self.postgres.get_next_network_id()

        self.assertTrue(del_result)
        self.assertEqual(next_result, 0)


                

if __name__ == '__main__':
    unittest.main()