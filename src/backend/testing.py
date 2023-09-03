import unittest
from MAC_table import MAC_table

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
        vendor = self.mac_table.find_vendor("00:00:00:00:00:00")
        self.assertEqual(vendor, "unknown")



























if __name__ == '__main__':
    unittest.main()