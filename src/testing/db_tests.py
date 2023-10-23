import unittest
import sys

sys.path.append("../backend")
from database import PostgreSQL_database
from response import Response

VALID_NETWORK_KEYS = ["network_id", "ssid", "gateway_mac", "name", "devices", "timestamp"]
VALID_NETWORK_VALUES = [1, "test_network_ssid", "12:34:56:78:90:AB", "test_network_name", {}, 0]
VALID_DEVICE_KEYS = ["mac", "ip", "mac_vendor", "os_family", "os_vendor", "os_type", "hostname", "parent", "website", "ports"]
VALID_DEVICE_VALUES = ["FE:DC:BA:09:87:65", "198.162.0.1", "test_vendor", "test_os", "test_os_vendor", "test_os_type", "test_host", "test_parent", "test", [22,80,500]]

# attempts to drop the test network
SQL_INJ_TEST =  """
                ;DELETE FROM networks
                WHERE network_id = 0;
                """

class DatabaseTester(unittest.TestCase):

    # before each
    def setUp(self):
        self.postgres = PostgreSQL_database("testing", "postgres", "root", "127.0.0.1", 5432)
        self.postgres.add_user({"username": "test","password":"test", "email":"test", "salt":""})
        self.user_id = self.postgres.get_user_by_login("test", "test").content["user_id"]
        
        # TODO
        # some dummy data to test queries
        self.postgres.save_network(self.user_id, self.get_test_network())

    # after each
    def tearDown(self):
        self.postgres.drop_db()

## ------------------------------------------------
##  helper functions
## ------------------------------------------------


    # checks my common sql injection phrase
    # returns True if the SQL injection does not work, False otherwise
    # i.e. we want this to be returning True
    def check_sql_inj(self) -> bool:
        return self.postgres.get_network(self.user_id, 0).status == 200
    
    # returns a test network to remain consistent
    def get_test_network(self) -> dict:
        network_vals = VALID_NETWORK_VALUES[:] # copy valid values
        network_vals[0] = 0
        return dict(zip(VALID_NETWORK_KEYS, network_vals))
        
## ------------------------------------------------
##  save_network tests
## ------------------------------------------------

    """
    Tests save_network with positive inputs
    Preconditions: PostgreSQL database exists
    Postconditions: Network successfully registered and added to the database
    """
    def test_save_net_pos(self):
        network = dict(zip(VALID_NETWORK_KEYS, VALID_NETWORK_VALUES))

        save_result = self.postgres.save_network(self.user_id, network)
        db_network = self.postgres.get_network(self.user_id, 1)

        self.assertEqual(save_result.content, 1)
        self.assertEqual(save_result.status, 200)
        self.assertEqual(db_network.content["network_id"], 1)
        self.assertEqual(db_network.status, 200)

    """
    Tests save_network with extra keys and values in the network
    Preconditions: PostgreSQL database exists
    Postconditions: Network successfully registered and added to the database
    """
    def test_save_net_pos_extra_key_vals(self):
        network_keys = VALID_NETWORK_KEYS + ["some", "dummy", "keys"]
        network_vals = VALID_NETWORK_VALUES + ["some", "dummy", "values"]
        network = dict(zip(network_keys, network_vals))

        save_result = self.postgres.save_network(self.user_id, network)
        db_network = self.postgres.get_network(self.user_id, 1)

        self.assertEqual(save_result.content, 1)
        self.assertEqual(save_result.status, 200)
        self.assertEqual(db_network.content["network_id"], 1)
        self.assertEqual(db_network.status, 200)
                
    """
    Tests save_network with invalid user_id
    Preconditions: PostgreSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_bad_user_id(self):
        network = dict(zip(VALID_NETWORK_KEYS, VALID_NETWORK_VALUES))

        save_result = self.postgres.save_network(self.user_id+1, network)
        db_network = self.postgres.get_network(self.user_id, 1) # need valid user_id to ensure network isn't added

        # db_error because user_id+1 is not a user in the database
        self.assertEqual(save_result.status, 500)
        self.assertEqual(save_result.message, Response.err_codes["db_error"][0])
        self.assertEqual(db_network.message, Response.err_codes["no_network"][0])
        self.assertEqual(db_network.status, 500)

    """
    Tests save_network with invalid user_id type
    Preconditions: PostgreSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_bad_user_id_type(self):
        network = dict(zip(VALID_NETWORK_KEYS, VALID_DEVICE_VALUES))

        # user_id as a string, testing implicit type conversions
        save_result = self.postgres.save_network(f"{self.user_id}", network) 
        db_network = self.postgres.get_network(self.user_id, 1) # need valid user_id to ensure network isn't added

        self.assertEqual(save_result.content, "")
        self.assertEqual(save_result.status, 500)
        self.assertEqual(db_network.content, "")
        self.assertEqual(db_network.status, 500)

    """
    Tests save_network with bad network key
    Preconditions: PostgreSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_neg_bad_key_name(self):
        network_keys = VALID_NETWORK_KEYS[:] # copy valid keys
        network_keys[2] = "bad_key"
        network = dict(zip(network_keys, VALID_NETWORK_VALUES))

        save_result = self.postgres.save_network(self.user_id, network)
        db_network = self.postgres.get_network(self.user_id, 1)

        self.assertEqual(save_result.status, 500)
        self.assertEqual(save_result.content, "")
        self.assertEqual(db_network.content, "")
        self.assertEqual(db_network.status, 500)

    """
    Tests save_network with bad network key type
    Preconditions: PostgreSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_neg_bad_key_type(self):
        network_keys = VALID_NETWORK_KEYS[:] # copy valid keys
        network_keys[2] = 3
        network = dict(zip(network_keys, VALID_NETWORK_VALUES))

        save_result = self.postgres.save_network(self.user_id, network)
        db_network = self.postgres.get_network(self.user_id, 1)

        self.assertEqual(save_result.status, 500)
        self.assertEqual(save_result.content, "")
        self.assertEqual(db_network.content, "")
        self.assertEqual(db_network.status, 500)

    """
    Tests save_network with a network id of chars
    Preconditions: PostgreSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_neg_bad_id_chars(self):
        network_vals = VALID_NETWORK_VALUES[:] # copy valid keys
        network_vals[0] = "bad"
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        save_result = self.postgres.save_network(self.user_id, network)
        db_network = self.postgres.get_network(self.user_id, 1)

        self.assertEqual(save_result.status, 500)
        self.assertEqual(save_result.content, "")
        self.assertEqual(db_network.content, "")
        self.assertEqual(db_network.status, 500)

    """
    Tests save_network with a network id < 0
    Preconditions: PostgreSQL database exists
    Postconditions: The database registered the network under a non negative id
    """
    def test_save_net_pos_negid(self):
        network_vals = VALID_NETWORK_VALUES
        network_vals[0] = -1
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        save_result = self.postgres.save_network(self.user_id, network)
        db_network_bad = self.postgres.get_network(self.user_id, -1)

        self.assertEqual(save_result.status, 200)
        self.assertEqual(db_network_bad.content, "")
        self.assertEqual(db_network_bad.status, 500)


    """
    Tests save_network with a malformed mac address
    Preconditions: PostgreSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_neg_bad_mac(self):
        network_vals = VALID_NETWORK_VALUES[:] # copy valid values
        network_vals[2] = "GG:PP:gg:oo:..:()"
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        save_result = self.postgres.save_network(self.user_id, network)
        db_network = self.postgres.get_network(self.user_id, 1)

        self.assertEqual(save_result.status, 500)
        self.assertEqual(save_result.content, "")
        self.assertEqual(db_network.status, 500)
        self.assertEqual(db_network.content, "")


    """
    Tests save_network for sql injection
    Preconditions: PostgreSQL database exists
    Postconditions: The database adds the network, but doesn't allow
                    SQL injection.
    """
    def test_save_net_neg_sql_inj(self):
        network_vals = VALID_NETWORK_VALUES[:] # copy valid values
        network_vals[1] = SQL_INJ_TEST
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        save_result = self.postgres.save_network(self.user_id, network)
        db_network = self.postgres.get_network(self.user_id, 1)
        
        self.assertTrue(self.check_sql_inj())
        self.assertEqual(save_result.status, 200)
        self.assertEqual(save_result.content, 1)
        self.assertEqual(db_network.status, 200)

    """
    Tests save_network with empty input
    Preconditions: PostgreSQL database exists
    Postconditions: The database did not register or add the network
    """
    def test_save_net_neg_empty(self):
        network = dict(zip([], []))

        save_result = self.postgres.save_network(self.user_id, network)
        
        self.assertEqual(save_result.status, 500)
        self.assertEqual(save_result.content, "")

    # Postconditions could be wrong, I'm unsure
    """
    Tests save_network with a duplicate ID
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database creates a new snapshot of the network
    """
    def test_save_net_pos_duplicate_id(self):

        # the test network is saved before each test,
        # here we try to save it a second time
        save_result = self.postgres.save_network(self.user_id, self.get_test_network())
        
        self.assertEqual(save_result.status, 200)
        self.assertEqual(save_result.content, 0)
        
    """
    Tests save_network with valid devices
    Preconditions: PostgreSQL database exsits
    Postconditions: The database creates a network with the devices
    """
    def test_save_net_pos_devices(self):

        device = dict(zip(VALID_DEVICE_KEYS, VALID_DEVICE_VALUES))
        network_vals = VALID_NETWORK_VALUES[:]
        network_vals[4] = {0:device}
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        save_result = self.postgres.save_network(self.user_id, network)
        contains_result = self.postgres.contains_device(1, device["mac"], 0)

        self.assertEqual(save_result.message, Response.err_codes["success"][0])
        self.assertEqual(save_result.status, 200)
        self.assertEqual(save_result.content, 1)
        self.assertTrue(contains_result)
    
    """
    Tests save_network with positive devices, ensuring case insensitive
    Preconditions: PostgreSQL database exists
    Postconditions: The database creates a newtork with the devices
    """
    def test_save_net_pos_case_sens_mac(self):
        device_vals = VALID_DEVICE_VALUES[:] # copy valid values
        device_vals[0] = "ab:CD:eF:12:34:56"
        device = dict(zip(VALID_DEVICE_KEYS, device_vals))

        network_vals = VALID_NETWORK_VALUES[:]
        network_vals[4] = {0:device}
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        save_result = self.postgres.save_network(self.user_id, network)
        contains_result = self.postgres.contains_device(1, device["mac"], 0)

        self.assertEqual(save_result.message, Response.err_codes["success"][0])
        self.assertEqual(save_result.status, 200)
        self.assertEqual(save_result.content, 1)
        self.assertTrue(contains_result)

    """
    Tests save_devices with multiple devices, some malformed (values), some good
    Preconditions: PostgreSQL database exists
    Postconditions: The database does not save the network, claiming malformed devices
    """
    def test_save_net_pos_bad_device_vals(self):
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

        network_vals = VALID_NETWORK_VALUES[:]
        network_vals[4] = devices
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        save_result = self.postgres.save_network(self.user_id, network)

        self.assertEqual(save_result.status, 500)
        self.assertEqual(save_result.message, Response.err_codes["malformed_device"][0])
    
        
    """
    Tests save_network with malformed device keys
    Preconditions: PostgreSQL Database exists
    Postconditions: Database doesn't add the network
    """
    def test_save_net_neg_bad_device_keys(self):
        device_keys = VALID_DEVICE_KEYS[:] # copy valid values
        device_keys[1] = "bad"
        device = dict(zip(device_keys, VALID_DEVICE_VALUES))

        network_vals = VALID_NETWORK_VALUES[:]
        network_vals[4] = {0:device}
        network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        save_result = self.postgres.save_network(self.user_id, network)
        
        self.assertEqual(save_result.status, 500)
        self.assertEqual(save_result.message, Response.err_codes["malformed_device"][0])

    # we may want to change the postconditions here
    """
    Tests save_network with devices that have malformed mac addresses
    Preconditions: PostgreSQL database exists
    Postconditions: Database adds the network, with only valid device macs
    """
    def test_save_net_neg_bad_mac(self):
        device_vals = VALID_DEVICE_VALUES[:] # copy valid values
        device = dict(zip(VALID_DEVICE_KEYS, device_vals))

        bad_macs = [
            "FG:QW:ZR:ET:XA:==",        # bad chars
            "1234567890ABCDEFabcdef",   # no :
            "123:abc:fff:ee:00:11",     # too many chars
            ":::::",                    # too few chars
        ]

        for bad_mac in bad_macs:

            device["mac"] = bad_mac
            
            network_vals = VALID_NETWORK_VALUES[:]
            network_vals[4] = {0: device}
            network = dict(zip(VALID_NETWORK_KEYS, network_vals))

            save_result = self.postgres.save_network(self.user_id, network)
            device_result = self.postgres.get_all_devices(self.user_id, 1)

            self.assertEqual(save_result.status, 500)
            self.assertEqual(save_result.message, Response.err_codes["malformed_device"][0])
            self.assertEqual(len(device_result.content), 0)

    # we may want to change the postconditions here
    """
    Tests save_network with devices that have malformed IP addresses
    Preconditions: PostgreSQL database exists
    Postconditions: Database adds the network, with only the valid devices
    """
    def test_save_net_pos_bad_ip(self):
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

            network_vals = VALID_NETWORK_VALUES[:]
            network_vals[4] = {0:device}
            network = dict(zip(VALID_NETWORK_KEYS, network_vals))

            save_result = self.postgres.save_network(self.user_id,network)
            device_result = self.postgres.get_all_devices(self.user_id, 1)

            self.assertEqual(save_result.status, 500)
            self.assertEqual(save_result.message, Response.err_codes["malformed_device"][0])
            self.assertEqual(len(device_result.content), 0)

## ------------------------------------------------
##  delete_network tests
## ------------------------------------------------

    """
    Tests delete_network with positive input
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database deletes the network successfully
    """
    def test_delete_network_pos(self):
        del_result = self.postgres.delete_network(self.user_id, 0)
        network_result = self.postgres.get_network(self.user_id, 0)
        networks_result = self.postgres.get_networks(self.user_id)

        self.assertEqual(del_result.status, 200)

        # This should probably just be a separate error code?
        # it would save checking the message. Or we could have the "no_network"
        # be another variable in Response
        self.assertEqual(network_result.status, 500)
        self.assertEqual(network_result.message, Response.err_codes["no_network"][0])

        self.assertEqual(len(networks_result.content), 0)
        self.assertEqual(networks_result.status, 200)

    """
    Tests delete_network with a non-existent network
    Preconditions: PostgreSQL database exists
    Postconditions: The database does nothing
    """
    def test_delete_network_neg_bad_network(self):
        del_result = self.postgres.delete_network(self.user_id, 1)
        networks_result = self.postgres.get_networks(self.user_id)

        self.assertEqual(del_result.status, 500)
        self.assertEqual(del_result.message, Response.err_codes["no_network"][0])

        self.assertEqual(len(networks_result.content), 1)
        self.assertEqual(networks_result.status, 200)

    """
    Tests delete_network with SQL injection
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: The database does not delete the network
                    and does not allow SQL injection
    """
    def test_delete_network_neg_sql_inj(self):

        del_result = self.postgres.delete_network(self.user_id, SQL_INJ_TEST)
        networks_result = self.postgres.get_networks(self.user_id)

        self.assertEqual(del_result.status, 500)
        self.assertEqual(del_result.message, Response.err_codes["bad_input"][0])

        self.assertEqual(networks_result.status, 200)
        self.assertEqual(len(networks_result.content), 1)

        self.assertTrue(self.check_sql_inj())

## ------------------------------------------------
##  validate_network_access
##  maybe this should be private?
## ------------------------------------------------

    """
    Tests validate_network_access with positive input
    Preconditions: PostreSQL database exists, network 0 exists
    Postconditions: The database agrees that the user has access to the network
    """
    def test_validate_net_access_pos(self):

        access_result = self.postgres.validate_network_access(self.user_id, 0)

        self.assertEqual(access_result.status, 200)

    """
    Tests validate_network_access with implicit access
    Preconditions: PostreSQL database exists, network 0 exists
    Postconditions: The database agrees that the user has access to the network
    """
    def test_validate_net_access_pos_implicit(self):
        access_result = self.postgres.validate_network_access(self.user_id, -1)

        self.assertEqual(access_result.status, 200)

    """
    Tests validate_network_access with non-existent network
    Preconditions: PostreSQL database exists, network 1 doesn't exists
    Postconditions: The database claims the network doesn't exist
    """
    def test_validate_net_access_neg_no_net(self):
        access_result = self.postgres.validate_network_access(self.user_id, 1)

        self.assertEqual(access_result.status, 500)
        self.assertEqual(access_result.message, Response.err_codes["no_network"][0])

    """
    Tests validate_network_access with non-existent user_id
    Preconditions: PostreSQL database exists, network 0 exists,
                user_id+1 doesn't have access to network 0
    Postconditions: The database claims the user doesn't have access
    """
    def test_validate_net_access_neg_no_access(self):
        access_result = self.postgres.validate_network_access(self.user_id+1, 0)

        self.assertEqual(access_result.status, 401)
        self.assertEqual(access_result.message, Response.err_codes["no_access"][0])

    """
    Tests validate_network_access with malformed user_id
    Preconditions: PostgreSQL database exists
    Postconditions: The database claims bad input
    """
    def test_validate_net_access_neg_bad_user(self):
        access_result = self.postgres.validate_network_access(f"{self.user_id}", 0)

        self.assertEqual(access_result.status, 500)
        self.assertEqual(access_result.message, Response.err_codes["bad_input"][0])

    """
    Tests validate_network_access with malformed network id
    Preconditions: PostgreSQL database exists
    Postconditions: The database claims bad input
    """
    def test_validate_net_access_neg_bad_net(self):
        access_result = self.postgres.validate_network_access(self.user_id, "0")

        self.assertEqual(access_result.status, 500)
        self.assertEqual(access_result.message, Response.err_codes["bad_input"][0])

    """
    Tests validate_network_access with sql injection
    Preconditions: PostgreSQL database exists
    Postconditions: The database doesn't allow sql injection
    """
    def test_validate_net_access_neg_sql_inj(self):
        access_result = self.postgres.validate_network_access(self.user_id, SQL_INJ_TEST)

        self.assertTrue(self.check_sql_inj())
        self.assertEqual(access_result.status, 500)
        self.assertEqual(access_result.message, Response.err_codes["bad_input"][0])

## ------------------------------------------------
##  contains_snapshot tests
## ------------------------------------------------

    """
    Tests contains_snapshot with positive input
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: contains_snapshot is true, nothing changes in database
    """
    def test_contains_snapshot_pos(self):
        contains_result = self.postgres.contains_snapshot(0,0)
        network_result = self.postgres.get_network(self.user_id, 0)

        self.assertTrue(contains_result)
        self.assertEqual(network_result.status, 200)
        self.assertEqual(network_result.content["network_id"], 0)
    
    """
    Tests contains_snapshot with non-existent network
    Preconditions: PostgreSQL database exists
    Postconditions: The database claims to not contain the snapshot
    """
    def test_contains_snapshot_neg_bad_network(self):
        contains_result = self.postgres.contains_snapshot(1,0)
        network_result = self.postgres.get_network(self.user_id, 1)

        self.assertFalse(contains_result)
        self.assertEqual(network_result.status, 500)
        self.assertEqual(network_result.message, Response.err_codes["no_network"][0])

    """
    Tests contains_snapshot with SQL injection
    Preconditions: PostgreSQL database exists
    Postconditions: The database claims bad input
    """
    def test_contains_snapshot_neg_sql_inj(self):
        contains_result = self.postgres.contains_snapshot(0, SQL_INJ_TEST)
        
        self.assertTrue(self.check_sql_inj())
        self.assertEqual(contains_result.status, 500)
        self.assertEqual(contains_result.message, Response.err_codes["bad_input"][0])

    """
    Tests contains_snapshot with bad network id
    Preconditions: PostgreSQL database exists
    Postconditions: The database claims bad input
    """
    def test_contains_snapshot_neg_bad_net_id(self):
        contains_result = self.postgres.contains_snapshot("0", 0)
        
        self.assertTrue(self.check_sql_inj())
        self.assertEqual(contains_result.status, 500)
        self.assertEqual(contains_result.message, Response.err_codes["bad_input"][0])

## ------------------------------------------------
##  get_networks tests
## ------------------------------------------------

    """
    Tests get_networks with one network
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: get_networks contains only newtork 0
    """
    def test_get_networks_pos(self):
        networks_result = self.postgres.get_networks(self.user_id)

        test_network = self.get_test_network()

        self.assertTrue(test_network in networks_result)
        self.assertEqual(networks_result.status, 200)
        self.assertEqual(len(networks_result.content), 1)

    """
    Tests get_networks with no networks
    Preconditions: PostgreSQL database exists,
                   networks table is empty - satisfied in this test
    Postconditions: get_networks returns an empty list
    """
    def test_get_networks_pos(self):
        self.postgres.delete_network(self.user_id, 0)
        networks_result = self.postgres.get_networks(self.user_id)

        self.assertEqual(networks_result.status, 200)
        self.assertEqual(len(networks_result.content), 0)

## ------------------------------------------------
##  get_network tests
## ------------------------------------------------


    """
    Tests get_network with an existing network
    Preconditions: PostgreSQL database exits, network 0 exists
    Postconditions: get_network returns the correct network
    """
    def test_get_network_pos(self):
        network_result = self.postgres.get_network(self.user_id, 0)

        self.assertEqual(network_result.content["network_id"], 0)
    
    # unsure if postconditions are correct, change if needed
    """
    Tests get_network with a network that isn't in the database
    Preconditions: PostgreSQL database exists
    Postconditions: get_network returns None
    """
    def test_get_network_neg_bad_network(self):
        network_result = self.postgres.get_network(self.user_id, 1)

        self.assertEqual(network_result.status, 500)
        self.assertEqual(network_result.message, Response.err_codes["no_network"][0])

    # unsure if postconditions are correct, change if needed
    """
    Tests get_network for SQL injection
    Preconditions: PostgreSQL database exists
    Postconditions: get_network returns None, and SQL injection fails
    """
    def test_get_network_neg_sql_inj(self):
        network_result = self.postgres.get_network(self.user_id, SQL_INJ_TEST)
        
        self.assertTrue(self.check_sql_inj())
        self.assertEqual(network_result.status, 500)
        self.assertEqual(network_result.message, Response.err_codes["bad_input"][0])

## ------------------------------------------------
##  rename_network tests
## ------------------------------------------------

    """
    Tests rename_network with positive input
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: rename_networks returns true, and successfully renames the network
    """
    def test_rename_network_pos(self):
        rename_result = self.postgres.rename_network(self.user_id, 0, "different_name")
        network_result = self.postgres.get_network(self.user_id, 0)

        self.assertEqual(rename_result.status, 200)
        self.assertEqual(network_result.content["network_id"], 0)

    """
    Tests rename_network on a non existent network
    Preconditions: PostgreSQL database exists
    Postconditions: rename_networks returns false, and does not rename any networks
    """
    def test_rename_network_neg_no_network(self):
        rename_result = self.postgres.rename_network(self.user_id, 0, "different_name")
        network_result = self.postgres.get_network(self.user_id, 0)

        self.assertEqual(rename_result.status, 200)
        self.assertEqual(network_result.content["network_id"], 0)

    """
    Tests rename_network for SQL injection
    Preconditions: PostgreSQL database exists, network 0 exists
    Postconditions: rename_network returns 0, doesn't rename the network,
                    and SQL injection fails
    """
    def test_rename_network_neg_sql_inj(self):
        rename_result = self.postgres.rename_network(self.user_id, 0, SQL_INJ_TEST)
        network_result = self.postgres.get_network(self.user_id, 0)

        self.assertEqual(network_result.content["network_id"], 0)
        self.assertTrue(self.check_sql_inj())
        self.assertEqual(rename_result.status, 200)


    # this should probably also be private I think
    # though, we likely should still test this one.
    def test_get_most_recent_ts_pos(self): pass
    def test_get_most_recent_ts_neg(self): pass

## ------------------------------------------------
##  get_all_devices tests
## ------------------------------------------------

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

        devices = {}

        for i, mac in enumerate(device_macs):
            device_vals[0] = mac
            device = dict(zip(device_keys, device_vals))

            devices[i] = device

        network_vals = VALID_NETWORK_VALUES[:] # copy valid values
        network_vals[4] = devices
        test_network = dict(zip(VALID_NETWORK_KEYS, network_vals))

        save_result = self.postgres.save_network(self.user_id, test_network)
        contains_results = [self.postgres.contains_device(1, device["mac"], 0) for device in devices.values()]
        devices_result = self.postgres.get_all_devices(self.user_id, 1)

        self.assertEqual(save_result.message, Response.err_codes["success"][0])
        self.assertEqual(save_result.status, 200)
        for result in contains_results:
            self.assertTrue(result)
        self.assertEqual(len(devices_result.content), 5)

    """
    Tests get_all_devices with empty network
    Preconditions: PostgreSQL database exists, network 0 exists and is empty
    Postconditions: get_all_devices returns an empty list
    """
    def test_get_all_devices_pos_empty(self):
        devices_result = self.postgres.get_all_devices(self.user_id,0)

        self.assertEqual(devices_result.status, 200)
        self.assertEqual(devices_result.content, [])

    """
    Tests get_all_devices for SQL injection
    Preconditions: PostgreSQL datbase exists, network 0 exists
    Postconditions: get_all_devices fails and does not
                    allow SQL injection
    """
    def test_get_all_devices_neg_sql_inj(self):
        devices_result = self.postgres.get_all_devices(self.user_id, SQL_INJ_TEST)
        
        self.assertTrue(self.check_sql_inj())
        self.assertEqual(devices_result.status, 500)

    # postcondition could be incorrect, change if needed
    """
    Tests get_all_devices on a non-existent network
    Preconditions: PostgreSQL datbase exists, network 1 does not exist
    Postconditions: get_all_devices fails
    """
    def test_get_all_devices_neg_no_network(self):
        devices_result = self.postgres.get_all_devices(self.user_id, 1)

        self.assertEqual(devices_result.status, 500)

## ------------------------------------------------
##  contains_device tests
## ------------------------------------------------

## ------------------------------------------------
##  get_snapshots tests
## ------------------------------------------------

## ------------------------------------------------
##  contains_snapshot tests
## ------------------------------------------------

## ------------------------------------------------
##  get_settings tests
## ------------------------------------------------

## ------------------------------------------------
##  set_settings tests
## ------------------------------------------------

## ------------------------------------------------
##  contains_user tests
## ------------------------------------------------

## ------------------------------------------------
##  add_user tests
## ------------------------------------------------

## ------------------------------------------------
##  get_user_by_login
## ------------------------------------------------

## ------------------------------------------------
##  get_user_by_id
## ------------------------------------------------

## ------------------------------------------------
##  get_salt_by_username
## ------------------------------------------------

## ------------------------------------------------
##  get_users
## ------------------------------------------------

## ------------------------------------------------
##  grant_access
## ------------------------------------------------

## ------------------------------------------------
##  drop_db
## ------------------------------------------------

                

if __name__ == '__main__':
    unittest.main()