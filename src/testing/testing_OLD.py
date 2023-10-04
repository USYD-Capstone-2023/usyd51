import unittest
import socket

from MAC_table import MAC_table
from db_dummy import db_dummy
from device import Device
from net_tools import get_dhcp_server_info, arp_helper, traceroute_helper, hostname_helper

def gen_valid_device():
    IP = "192.168.0.1"
    MAC = "E8:0A:B9:9D:68:16"
    d = Device(IP, MAC)
    return d
    #ip = "unknown"
    #mac = "unknown"
    #mac_vendor = "unknown"
    #os_family = "unknown"
    #os_vendor = "unknown"
    #os_type = "unknown"
    #hostname = "unknown"
    #parent = "unknown"

def get_ip_address():
        try:
            # Create a socket object to get the local hostname
            hostname = socket.gethostname()
            # Get the IP address associated with the local hostname
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except Exception as e:
            return str(e)

class test_MAC_table(unittest.TestCase):

    # Set up before each test

    def setUp(self):
        mac_table_fp = "../cache/oui.csv"
        self.mac_table = MAC_table(mac_table_fp)  # Provide a test CSV file for your MAC table data

    # Test the find_vendor method
    def test_find_vendor_known(self):
        # Test a known MAC address
        vendor = self.mac_table.find_vendor("E8:0A:B9:9D:68:16")
        self.assertEqual(vendor, "Cisco Systems, Inc")

    def test_find_vendor_unknown(self):
        # Test an unknown MAC address
        vendor = self.mac_table.find_vendor("FF:FF:FF:FF:FF:FF")
        self.assertEqual(vendor, "unknown")

class TestDbDummy(unittest.TestCase):

    def setUp(self):
        # Create an instance of the db_dummy class for testing
        self.db = db_dummy("test_db", "test_user", "test_password")

    def tearDown(self):
        # Clean up resources after each test if needed
        pass

    def test_contains_mac_known(self):
        network_id = "network1"
        mac = "00:0A:95:9D:68:16"

        # Test when the MAC exists in the network
        self.db.devices[network_id] = {mac: gen_valid_device()}
        result = self.db.contains_mac(mac, network_id)
        self.assertTrue(result)

    def test_contains_mac_unknown(self):
        network_id = "network1"

        # Test when the MAC does not exist in the network
        result = self.db.contains_mac("non_existent_mac", network_id)
        self.assertFalse(result)

    def test_save_device_known(self):
        network_id = "network1"
        device = gen_valid_device()

        # Test saving a device
        self.db.save_device(device, network_id)
        self.assertEqual(self.db.devices[network_id][device.mac], device)

    def test_get_device_known(self):
        network_id = "network1"
        mac = "00:0A:95:9D:68:16"
        device = gen_valid_device()

        # Test getting a device
        self.db.devices[network_id] = {mac: device}
        result = self.db.get_device(network_id, mac)
        self.assertEqual(result, device)

    def test_get_device_unknown(self):
        self.db.TESTING_WIPE_DATABASE()
        network_id = "network1"
        mac = "00:0A:95:9D:68:16"

        # Test getting a device that doesn't exist
        self.db.register_network(network_id)
        with self.assertRaises(KeyError):
            print(self.db.get_device(network_id, mac))

    def test_register_network_known(self):
        network_id = "network1"

        # Test registering a network
        self.db.register_network(network_id)
        self.assertTrue(network_id in self.db.devices)

    def test_register_network_unknown(self):
        network_id = "network1"

        # Test registering a network that already exists
        self.db.devices[network_id] = {}
        #with self.assertRaises(KeyError):
            #self.db.register_network(network_id)

    def test_get_all_devices_known(self):
        network_id = "network1"
        devices = {"mac1": gen_valid_device(), "mac2": gen_valid_device()}

        # Test getting all devices in a network
        self.db.devices[network_id] = devices
        result = self.db.get_all_devices(network_id)
        self.assertEqual(result, devices)

    def test_add_device_known(self):
        network_id = "network1"
        device = gen_valid_device()

        # Test adding a device
        self.db.register_network(network_id)
        self.db.add_device(device, network_id)
        self.assertEqual(self.db.devices[network_id][device.mac], device)

    def test_add_device_parent_known(self):
        network_id = "network1"
        device = gen_valid_device()
        parent = "parent_device"

        # Test adding a device with a parent
        self.db.devices[network_id] = {device.mac: device}
        self.db.add_device_parent(device, network_id, parent)
        self.assertEqual(self.db.devices[network_id][device.mac].parent, parent)

class test_device(unittest.TestCase):

    def test_device_json(self):
        device = gen_valid_device()
        self.assertEqual(device.to_json(), {"mac" : device.mac, "ip" : device.ip, "mac_vendor" : device.mac_vendor, "os_family" : device.os_family, "os_vendor" : device.os_vendor, "os_type" : device.os_type, "hostname" : device.hostname, "parent" : device.parent})

class test_net_tools(unittest.TestCase):

    def test_ARP_scan_known(self):
        DHCP_info = get_dhcp_server_info()
        ip, mac = arp_helper(DHCP_info["router"])
        self.assertEqual(ip, DHCP_info["router"])
        self.assertIsNotNone(mac)
    
    def test_ARP_scan_unknown(self):
        external_ip = "8.8.8.8"
        ip, mac = arp_helper(external_ip)
        self.assertIsNone(ip)
        self.assertIsNone(mac)
    
    def test_traceroute_helper_known(self):
        gateway = get_dhcp_server_info()["router"]
        self.assertIsNotNone(traceroute_helper([get_ip_address(),gateway]))
    
    def test_hostname_helper_known(self):
        hostname = socket.gethostname()
        self.assertEqual(hostname, hostname_helper(get_ip_address())[:len(hostname)])
    
    def test_hostname_helper_unknown(self):
        self.assertEqual("unknown", hostname_helper("8.8.8.8.8"))

    def test_DHCP_server_info(self):
        self.assertIsNotNone(get_dhcp_server_info())


if __name__ == '__main__':
    unittest.main()