import csv, os

class MACTable:

    mac_table = {}

    def __init__(self, filepath):

        # For windows support change direction of slashes
        if os.name == "nt":
            filepath = filepath.replace("/", "\\")

        try:
            with open(filepath, encoding = "utf-8") as f:

                reader = csv.reader(f)
                for line in reader:
                    if len(line) < 3:
                        continue

                    self.mac_table[line[1]] = line[2]

        except FileNotFoundError as e:
            print("[ERROR] Failed to read MAC table from file... Continuing without MAC lookup.")
            print(e)

    # Resolves the vendor of a device based on its mac address
    def find_vendor(self, mac_address):

        if mac_address == None:
            return "unknown"

        oui = "".join([x for x in mac_address.split(":")[:3]]).upper()
        if oui in self.mac_table.keys():
            return self.mac_table[oui]

        return "unknown"


########################### DEPRECATED DUE TO ADDED COMPLEXITY ################################
# wget library, requests and urllib struggle to consistently download the oui table and so Im 
# disabling this feature for now.
# 
# TIMEOUT = 10
# initialized = False
# 
# # Retrieves the MAC -> Vendor lookup table
# def init_mac_table(self, filepath):
# 
#     dir = "".join([x + "/" for x in filepath.split("/")[:-1]])
#     if os.name == "nt":
#         dir = dir.replace("/", "\\")
# 
#     if not os.path.exists(dir):
#         os.makedirs(dir)
# 
#     print("[INFO] Fetching MAC vendors table, please wait...")
# 
#     refresh = True
# 
#     date_format = "%d/%m/%Y"
#     today = datetime.datetime.now()
# 
#     # Checks if the cached MAC table was downloaded in the past 7 days
#     try:
#         with open(filepath, "r") as f:
#             reader = csv.reader(f)
#             row = next(reader)
#             if row:
#                 delta = today - datetime.datetime.strptime(row[0], date_format)
#                 if delta.days < 7:
#                     refresh = False
#                 else:
#                     print("[INFO] MAC cache file is out of date.")
# 
#     except Exception as e:
#         print("[WARNING] Could not read or locate MAC table cache file.")
#         print(e)
# 
#     # Downloads the updated OUI table from IEEE, saves to cache file
#     if refresh:
# 
#         print("[INFO] Retrieving table from 'https://standards-oui.ieee.org'")
#         try:
#             tmp_fp = filepath + ".tmp"
#             wget.download(https://standards-oui.ieee.org/oui/oui.csv, out=tmp_fp)
# 
#             # This posts charmap decode error on windows TODO
#             with open(tmp_fp, 'r+') as f:
#                 content = f.read()
#                 f.seek(0, 0)
#                 f.write(today.strftime(date_format) + "\n")
# 
#             os.rename(tmp_fp, filepath)
# 
#         except Exception as e:
#             print("\n[ERROR] A network error occurred.")
#             print(e)
#             # TODO - Add cleanup for unconfirmed (downloading) tempfiles 
# 
#     # Read mac table data from cache file
#     print("[INFO] Reading MAC table from cache file.")
#     try:
#         # Skip first two rows of header information
#         skip = 2
#         with open(filepath, "r") as f:
# 
#             reader = csv.reader(f)
#             for line in reader:
#                 if skip > 0:
#                     skip -= 1
#                     continue
# 
#                 if len(line) < 3:
#                     continue
# 
#                 self.mac_table[line[1]] = line[2]
# 
#     except Exception as e:
#         print("[ERROR] Failed to read MAC table from file... Continuing without MAC lookup.")
#         print(e)