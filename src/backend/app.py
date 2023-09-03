# External
from flask import Flask
from scapy.all import Ether, conf, get_if_addr

# Local
from MAC_table import MAC_table
from loading_bar import Loading_bar
from job import Job
from threadpool import Threadpool
from device import Device
from net_tools import *
# from database import PostgreSQLDatabase
from db_dummy import db_dummy

# Stdlib
import time, threading, socket, os, signal, sys

MAC_TABLE_FP = "../cache/oui.csv"
NUM_THREADS = 25

# Ensures that the user has root perms uf run on posix system.
if os.name == "posix" and os.geteuid() != 0: 
    print("Root permissions are required for this program to run.")
    quit()

app = Flask(__name__)

# Retrieves dhcp server information (router ip, subnet mask, domain name)
print("[INFO] Retrieveing DHCP server info...")
dhcp_server_info = get_dhcp_server_info()

if dhcp_server_info["router"] == None:
    print("[ERR ] Unable to determine default gateway, are you connected to the internet?\nExitting...")
    sys.exit()

gateway = dhcp_server_info["router"]
gateway_hostname = dhcp_server_info["domain"]

# Initialise mac lookup table, loading bar and threadpool
mac_table = MAC_table(MAC_TABLE_FP)
lb = Loading_bar()
threadpool = Threadpool(NUM_THREADS)

# Init db, temporary fake db for development
db = db_dummy("networks", "temp_username", "temp_password")
# db = PostgreSQLDatabase("networks", "temp_username", "temp_password")

# Creates a new table in the database for the current network
gateway_mac = arp_helper(gateway)[1]
db.register_network(gateway_mac)

# Creates a device object for the client device
client_device = Device(get_if_addr(conf.iface), Ether().src)
client_device.hostname = socket.gethostname()
client_device.mac_vendor = mac_table.find_vendor(client_device.mac)
db.add_device(client_device, gateway_mac)

# Creates device object to represent the gateway
gateway_device = Device(gateway, gateway_mac)
gateway_device.hostname = gateway_hostname
db.add_device(gateway_device, gateway_mac)


# Signal handler to gracefully end the threadpool on shutdown
def cleanup(*args,):
    threadpool.end()
    print("Finished cleaning up! Server will now shut down.")
    sys.exit()

signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)


# Updates the mac vendor field of all devices in the current network's table of the database 
def get_mac_vendors():

    devices = db.get_all_devices(gateway_mac)

    lb.set_params("Resolving MAC Vendors", 40, len(devices.keys()))
    lb.show()

    for device in devices.values():
        device.mac_vendor = mac_table.find_vendor(device.mac)
        db.save_device(device, gateway_mac)
        lb.increment()
        lb.show()

    lb.reset()


# Performs a reverse DNS lookup on all devices in the current network's table of the database 
@app.get("/hostname")
def get_hostnames():

    devices = db.get_all_devices(gateway_mac)
    returns = [-1] * len(devices.keys())
    
    lb.set_params("Resolving Hostnames", 40, len(devices.keys()))
    lb.show()

    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]
    dispatched = len(devices.keys())
    job_counter = 0
    for device in devices.values():

        # If hostname has been found in wlan DNSRR sniffer use it instead
        if device.hostname != "unknown":
            lb.increment()
            dispatched -= 1
            returns[job_counter] = device.hostname
            job_counter += 1
            continue

        job = Job(fptr=hostname_helper, args=device.ip, ret_ls=returns, ret_id=job_counter, counter_ptr=counter_ptr, cond=cond)
        job_counter += 1
        if not threadpool.add_job(job):
                                
            return "Request size over maximum allowed size %d" % (threadpool.MAX_QUEUE_SIZE)

    mutex.acquire()
    while counter_ptr[0] < dispatched:
        cond.wait()
        lb.set_progress(counter_ptr[0] + (len(devices.keys()) - dispatched))
        lb.show()
    mutex.release()

    ret = {}
    job_counter = 0
    for device in devices.values():

        if device.hostname != "unkown":
            device.hostname = returns[job_counter]
            db.save_device(device, gateway_mac)
        job_counter += 1

    lb.reset()
    

# Runs a traceroute on all devices in the database to get their neighbours in the routing path
def traceroute_all():
        

    devices = db.get_all_devices(gateway_mac)
    device_addrs = set()

    print("[INFO] Tracing Routes...")
    lb.set_params("Tracing routes to devices", 40, len(devices.keys()))
    lb.show()
    
    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]
    returns = [-1] * len(devices.keys())

    # Creates a thread job to do traceroute on all devices, adds them to threadpool queue
    job_counter = 0
    for device in devices.values():

        device_addrs.add(device.ip)

        job = Job(fptr=traceroute_helper, args=(device.ip, gateway), ret_ls=returns, ret_id=job_counter, counter_ptr=counter_ptr, cond=cond)
        job_counter += 1
        if not threadpool.add_job(job):

            returns = None
            return "Request size over maximum allowed size %d" % (threadpool.MAX_QUEUE_SIZE)

    # Waits for all jobs to be completed by the threadpool
    mutex.acquire()
    while counter_ptr[0] < len(devices.keys()):
        cond.wait()
        lb.set_progress(counter_ptr[0])
        lb.show()

    mutex.release()
    print("\n[INFO] Traceroute complete!\n")

    # Parses output
    job_counter = 0
    for device in devices.values():

        parent = ""
        for addr in returns[job_counter]:
            # Adds devices to database if they don't already exist
            if addr not in device_addrs:
                device_addrs.add(addr)
                new_device = Device(addr, arp_helper(addr)[1])
                new_device.parent = parent
                db.add_device(new_device)
                devices = db.get_all_devices(gateway_mac)

            parent = addr

        # Updates the devices parent node
        if len(returns[job_counter]) >= 2:
            db.add_device_parent(device, gateway_mac, returns[job_counter][-2])
            
        job_counter += 1
    
    returns = None
    lb.reset()


# Gets all devices on the network
def get_devices():

    subnet_mask = dhcp_server_info["subnet_mask"]
    
    # Breaks subnet and gateway ip into bytes
    sm_split = subnet_mask.split(".")
    gateway_split = gateway.split(".")
    first_ip = [0] * 4
    last_ip = [0] * 4

    # Calculates first and last IPs byte by byte, based off subnet mask and router IP
    for i in range(4):
        sm_chunk = int(sm_split[i])
        gateway_chunk = int(gateway_split[i])

        first_ip[i] = sm_chunk & gateway_chunk
        sm_inv = (1 << 8) - 1 - sm_chunk
        last_ip[i] = sm_inv | (sm_chunk & gateway_chunk)

    print("[INFO] Getting all active devices on network.")

    # Generates return array of size equal to the number of IPs in the range
    num_addrs = 1
    for i in range(4):
        num_addrs *= max(last_ip[i] - first_ip[i] + 1, 1) 

    returns = [-1] * num_addrs
    
    lb.set_params("Scanning for active devices", 40, num_addrs)
    lb.show()

    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]

    # Runs an arp scan on all IPs in the networks ip range
    id = 0
    for p1 in range(first_ip[0], last_ip[0] + 1):
        for p2 in range(first_ip[1], last_ip[1] + 1):
            for p3 in range(first_ip[2], last_ip[2] + 1):
                for p4 in range(first_ip[3], last_ip[3] + 1):

                    ip = "%d.%d.%d.%d" % (p1, p2, p3, p4)

                    job = Job(fptr=arp_helper, args=ip, ret_ls=returns, ret_id=id, counter_ptr=counter_ptr, cond=cond)
                    id += 1
                    if not threadpool.add_job(job):

                        returns = None
                        return "Request size over maximum allowed size %d" % (threadpool.MAX_QUEUE_SIZE)
                    
    # Waits for all tasks to be completed by the threadpool
    mutex.acquire()
    while counter_ptr[0] < num_addrs:
        cond.wait()
        lb.set_progress(counter_ptr[0])
        lb.show()

    mutex.release()

    # Creates a device object for each ip and mac, saves to database
    for i in range(num_addrs):
        ip = returns[i][0]
        mac = returns[i][1]
        if mac and ip and not db.contains_mac(mac, gateway_mac):
            db.add_device(Device(ip, mac), gateway_mac)

    print("\n[INFO] Found %d devices!\n" % (len(db.get_all_devices(gateway_mac).keys())))
    returns = None
    lb.reset()


# Gives all the information about the current network that is stored in the database, does not re-run scans
@app.get("/get_devices_no_update")
def current_devices():

    devices = db.get_all_devices(gateway_mac)

    ret = {}
    for device in devices.values():
        ret[device.mac] = device.to_json(); 
    return ret


# Finds all devices on the network, traces routes to all of them, resolves mac vendors and hostnames.
# Serves the main mapping data for the program
@app.get("/map_network")
def map_network():

    get_devices()
    traceroute_all()
    get_mac_vendors()
    get_hostnames()

    return current_devices()

  
# Gets the OS information of the given ip address through TCP fingerprinting
@app.get("/os_info")
def os_scan():

    print("[INFO] Getting OS info...")

    devices = db.get_all_devices(gateway_mac)
    returns = [-1] * len(devices.keys())
    
    lb.set_params("Scanned", 40, len(devices.keys()))
    lb.show()

    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]

    # Creates a thread task to scan each devices OS, adds to threadpool queue
    job_id = 0
    for device in devices.values():

        job = Job(fptr=os_helper, args=device.ip, ret_ls=returns, ret_id=job_id, counter_ptr=counter_ptr, cond=cond)
        job_id += 1
        if not threadpool.add_job(job):

            returns = None
            return "Request size over maximum allowed size %d" % (threadpool.MAX_QUEUE_SIZE)

    # Waits for all jobs to be completed
    mutex.acquire()
    while counter_ptr[0] < len(devices.keys()):
        cond.wait()
        lb.set_progress(counter_ptr[0])
        lb.show()

    mutex.release()
    print("\n[INFO] OS scan complete!\n")

    # Sets all devices OS information
    job_id = 0
    for device in devices.values():
        device.os_type = returns[job_id]["os_type"]
        device.os_family = returns[job_id]["os_family"]
        device.os_vendor = returns[job_id]["os_vendor"]
        job_id += 1
    
    returns = None


# Serves the information of the dhcp server
@app.get("/dhcp_info")
def serve_dhcp_server_info():

    return dhcp_server_info


# Returns the progress and data of the current loading bar.
# Polled by frontend to update ui loading bars in electron  
@app.get("/request_progress")
def get_current_progress():

    if lb.total_value == 0:
        return {"flag" : False}

    return {"flag" : True, "progress" : lb.counter, "total" : lb.total_value, "label" : lb.label}















