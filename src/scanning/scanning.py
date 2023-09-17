import  sys

# External
import requests

# Local
import net_tools as nt

# Stdlib
import os, json

SETTINGS_FILEPATH = "./settings.json"

# TODO send loading bar info to node over FIFO


if os.name == "nt":
    SETTINGS_FILEPATH = SETTINGS_FILEPATH.replace("/", "\\")


def set_default_settings():

    default_settings = """
{
    "TCP":true,
    "UDP":true, 
    "ports": [22,23,80,443],

    "run_ports": false,
    "run_os": false,
    "run_hostname": true,
    "run_mac_vendor": true,
    "run_trace": true,
    "run_vertical_trace": true,

    "defaultView": "grid",
    "defaultNodeColour": "0FF54A",
    "defaultEdgeColour": "32FFAB",
    "defaultBackgroundColour": "320000"
}"""

    with open(SETTINGS_FILEPATH, "w") as f:
        f.write(default_settings)

# Finds all devices on the network, traces routes to all of them, resolves mac vendors and hostnames.
# If a valid network id is entered, it will add the scan results to the database under that ID with a new timestamp,
# otherwise will create a new network in the db
def scan_network(network_id=-1):

    settings_json = ""
    with open(SETTINGS_FILEPATH, "r") as f:
        settings_json = f.read()

    settings = json.loads(settings_json)

    require = ["run_trace", "run_hostname", "run_vertical_trace", "run_mac_vendor",
               "run_os", "run_ports", "ports"]
    
    args = []
    for req in require:
        if req not in settings.keys():
            print("[ERR ] Malformed settings file, missing required field: %s. Reverting to default settings file." % (req))
            set_default_settings()
            scan_network(network_id)
            return
        
        args.append(settings[req])


    nt.scan(network_id, *args)

# Serves the information of the dhcp server
def get_dhcp_server_info():

    # TODO send to node through FIFO maybe?
    return print(nt.get_dhcp_server_info())


def get_current_ssid():

    # TODO send to node through FIFO maybe?
    return nt.get_ssid()


if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("Must provide scan type as an argument. Exitting.")
        sys.exit(-1)

    # Ensures that the user has root perms uf run on posix system.
    if os.name == "posix" and os.geteuid() != 0: 
        print("Root permissions are required for this program to run.")
        quit()

    if not os.path.exists(SETTINGS_FILEPATH):

        set_default_settings()
            
    # Initialise loading bar, network utilities and mac vendor lookup table

    options = {
        "scan_network" : scan_network,
        "ssid" : get_current_ssid,
        "dhcp" : get_dhcp_server_info
    }

    if sys.argv[1] not in options.keys():
        print("[ERR ] Provided operation is not valid: %s" % (sys.argv[1]))
        sys.exit(-1)

    options[sys.argv[1]](*sys.argv[2:])

