import  sys

# External
import requests

# Local
import net_tools as nt

# Stdlib
import os

NUM_THREADS = 25
BACKEND_URL = "http://127.0.0.1:5000"

# Finds all devices on the network, traces routes to all of them, resolves mac vendors and hostnames.
# Serves the main mapping data for the program
def map_network():

    network = nt.basic_scan()
    requests.put(BACKEND_URL + "/network/add", json=network)


# Rescans an existing network
def rescan_network(network_id):

    nt.basic_scan(network_id)


# Gets the OS information of the given ip address through TCP fingerprinting
def os_scan():

    nt.add_os_info()


# Serves the information of the dhcp server
def get_dhcp_server_info():

    return nt.get_dhcp_server_info()


def get_ssid():

    return nt.get_ssid()


def port_scan(network_id):

    nt.add_ports(network_id)


def savesettings():
    '''
    assuming save settings are in a JSON format
    {
    "TCP":True,
    "UDP":True, 
    "ports": [22,23,80,443],

    "DefaultSave": True,

    "attemptPortScan": False,
    "attemptArp": False,
    "attemptOS": False,
    "attemptDNS": False,
    "attemptTraceroute": True,

    "defaultView": "grid",
    "defaultNodeColour": "0FF54A",
    "defaultEdgeColour": "32FFAB",
    "defaultBackgroundColour": "320000",
    }
    '''
    try:
        # Get the JSON data from the request
        data = request.get_json()  
        print("Received data:", data)
        return "Settings saved successfully.", 200
    except Exception as e:
        print("Error:", str(e))
        return "Error saving settings.", 500


if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("Must provide scan type as an argument. Exitting.")
        sys.exit(-1)

    # Ensures that the user has root perms uf run on posix system.
    if os.name == "posix" and os.geteuid() != 0: 
        print("Root permissions are required for this program to run.")
        quit()

    if NUM_THREADS < 1:
        print("[ERR ] Thread count cannot be less than 1. Exitting...")
        sys.exit(-1)

    # Initialise loading bar, network utilities and mac vendor lookup table

    options = {
        "new_network" : map_network,
        "rescan_network" : rescan_network,
        "os_scan" : os_scan,
        "port_scan" : port_scan,
        "ssid" : get_ssid,
        "dhcp" : get_dhcp_server_info
    }

    if sys.argv[1] not in options.keys():
        print("[ERR ] Provided operation is not valid: %s" % (sys.argv[1]))
        sys.exit(-1)

    options[sys.argv[1]](*sys.argv[2:])

