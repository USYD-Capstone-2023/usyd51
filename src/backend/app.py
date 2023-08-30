# External
from flask import Flask
from scapy.all import *

# Local
from MAC_table import MAC_table
from loading_bar import Loading_bar
from job import Job
from threadpool import Threadpool
from DHCP_info import get_dhcp_server_info
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

# Init db, temporary fake db for development
db = db_dummy("networks", "temp_username", "temp_password")
# db = PostgreSQLDatabase("networks", "temp_username", "temp_password")

mac_table = MAC_table(MAC_TABLE_FP)
lb = Loading_bar()
threadpool = Threadpool(NUM_THREADS)

# Default value, gets resolved on initialization by DHCP server
gateway = "192.168.1.1"
gateway_hostname = "unknown"
print("[INFO] Retrieveing DHCP server info...")

# Retrieves network information (subnet mask, router ip, dns ip, timeserver ip, etc)
dhcp_server_info = get_dhcp_server_info()
if "error" not in dhcp_server_info.keys() and len(dhcp_server_info.keys()) > 1:
    gateway = dhcp_server_info["router"]
    gateway_hostname = dhcp_server_info["domain"]

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


# Seems to only work on some networks, potentially a proxy or firewall issue.
# ---------------------------------------- WIP -----------------------------------------
# packet sniffing daemon to get hostnames
# def wlan_sniffer_callback(pkt):

#     # Sniffs mDNS responses for new hostnames
#     if IP in pkt and UDP in pkt and pkt[UDP].dport == 5353:

#         if DNSRR in pkt:
#             name = pkt[DNSRR].rrname.decode("utf-8")
#             print(name)
#             if name.split(".")[-2] != "arpa" and name[0] != "_":

#                 ip = pkt[IP].src
#                 mac = arp_helper(ip)[1]

#                 if not db.contains_mac(mac, gateway_mac):
#                     device = Device(ip, mac)
#                     device.hostname = name
#                     db.add_device(device, gateway_mac)
#                 else:
#                     device = db.get_device(gateway_mac, mac)
#                     device.hostname = name
#                     db.save_device(device, gateway_mac)


# def run_wlan_sniffer(iface):
#     sniff(prn=wlan_sniffer_callback, iface=iface)

# DNS_sniffer = threading.Thread(target=run_wlan_sniffer, args=(conf.iface,))
# DNS_sniffer.daemon = True
# DNS_sniffer.start()

# ---------------------------------------- END WIP --------------------------------------


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

# Active DNS, LLMNR, MDNS requests, cant get these to work at the minute but theyll be useful
# ---------------------------------------- WIP -----------------------------------------

        # iface = conf.iface

        # host_rev = "".join(["%s." % x for x in host.split(".")[::-1]]) + "in-addr.arpa"

        # query = Ether(src=own_mac, dst="FF:FF:FF:FF:FF:FF") / \
        #         IP(src=own_ip, dst="224.0.0.252") / \
        #         UDP(sport=60403, dport=5355)/ \
        #         LLMNRQuery(id=1, qd=DNSQR(qname=host_rev, qtype="PTR", qclass="IN"))

        # response = srp1(query)

        # if response and LLMNRResponse in response:
        #     name = response[LLMNRResponse].qd.qname.decode()
        #     print("resolved hostname: %s" % (name))
        #     print("ip: %d" % (response[LLMNRResponse].an.rdata))
        #     ret[host] = name

        # print(ret[host])

        # mdns_ip = "224.0.0.251"
        # mdns_mac = "01:00:5e:00:00:fb"

        # mdns_query = Ether(src=own_mac, dst=mdns_mac) / \
        #              IP(src=own_ip, dst=mdns_ip) / \
        #              UDP(sport=5353, dport=5353) / \
        #              DNS(rd=1, qd=DNSQR(qname=host_rev, qtype="PTR"))

        # responses, _ = srp(mdns_query, verbose=0, timeout=2)

        # for response in responses:
        #     if DNSRR in response[1] and response[1][DNSRR].type == 12:
        #         name = response[1][DNSRR].rdata.decode()
        #         print("resolved hostname: %s" % (name))
        #         ret[host] = name

        # print(ret[host])
        # try:
        #     ret[host] = socket.gethostbyaddr(host)
        # except:
        #     ret[host] = "unknown"
# ---------------------------------------- WIP -----------------------------------------
    

def traceroute_all():
        
    print("[INFO] Tracing Routes...")

    devices = db.get_all_devices(gateway_mac)

    returns = [-1] * len(devices.keys())
    
    lb.set_params("Tracing routes to devices", 40, len(devices.keys()))
    lb.show()
    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]

    job_counter = 0
    for device in devices.values():

        job = Job(fptr=traceroute_helper, args=(device.ip, gateway), ret_ls=returns, ret_id=job_counter, counter_ptr=counter_ptr, cond=cond)
        job_counter += 1
        if not threadpool.add_job(job):

            returns = None
            return "Request size over maximum allowed size %d" % (threadpool.MAX_QUEUE_SIZE)


    mutex.acquire()
    while counter_ptr[0] < len(devices.keys()):
        cond.wait()
        lb.set_progress(counter_ptr[0])
        lb.show()

    mutex.release()
    print("\n[INFO] Traceroute complete!\n")

    job_counter = 0
    for device in devices.values():
        db.add_device_route(device, gateway_mac, returns[job_counter])
        job_counter += 1
    
    returns = None
    lb.reset()


def get_devices():

      # Default
    subnet_mask = "255.255.255.0"
    if "subnet_mask" in dhcp_server_info.keys():
        subnet_mask = dhcp_server_info["subnet_mask"]
    
    sm_split = subnet_mask.split(".")
    gateway_split = gateway.split(".")
    first_ip = [0] * 4
    last_ip = [0] * 4

    for i in range(4):
        sm_chunk = int(sm_split[i])
        gateway_chunk = int(gateway_split[i])

        first_ip[i] = sm_chunk & gateway_chunk
        sm_inv = (1 << 8) - 1 - sm_chunk
        last_ip[i] = sm_inv | (sm_chunk & gateway_chunk)

    print("[INFO] Getting all active devices on network.")

    num_addrs = 1
    for i in range(4):
        num_addrs *= max(last_ip[i] - first_ip[i] + 1, 1) 

    returns = [-1] * num_addrs
    
    lb.set_params("Scanning for active devices", 40, num_addrs)
    lb.show()

    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]

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
                    

    mutex.acquire()
    while counter_ptr[0] < num_addrs:
        cond.wait()
        lb.set_progress(counter_ptr[0])
        lb.show()

    mutex.release()

    for i in range(num_addrs):
        ip = returns[i][0]
        mac = returns[i][1]
        if mac and ip and not db.contains_mac(mac, gateway_mac):
            db.add_device(Device(ip, mac), gateway_mac)

    print("\n[INFO] Found %d devices!\n" % (len(db.get_all_devices(gateway_mac).keys())))
    returns = None
    lb.reset()


# Gets the IP and MAC of all devices currently active on the network 
@app.get("/map_network")
def map_network():

    get_devices()
    traceroute_all()
    get_mac_vendors()
    get_hostnames()

    devices = db.get_all_devices(gateway_mac)

    ret = {}
    for device in devices.values():
        ret[device.mac] = device.to_json(); 
    return ret

  
# Gets the OS information of the given ip address through TCP fingerprinting
@app.get("/os_info/<macs>")
def os_scan(macs):

    print("[INFO] Getting OS info...")

    macs = macs.split(",")
    returns = [-1] * len(macs)
    
    lb.set_params("Scanned", 40, len(macs))
    lb.show()

    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]

    job_id = 0
    for mac in macs:

        job = Job(fptr=os_helper, args=devices[mac].ip, ret_ls=returns, ret_id=job_id, counter_ptr=counter_ptr, cond=cond)
        job_id += 1
        if not threadpool.add_job(job):

            returns = None
            return "Request size over maximum allowed size %d" % (threadpool.MAX_QUEUE_SIZE)

    mutex.acquire()
    while counter_ptr[0] < len(macs):
        cond.wait()
        lb.set_progress(counter_ptr[0])
        lb.show()

    mutex.release()
    print("\n[INFO] OS scan complete!\n")

    job_id = 0
    for mac in macs:
        devices[mac].os_type = returns[job_id]["os_type"]
        devices[mac].os_family = returns[job_id]["os_family"]
        devices[mac].os_vendor = returns[job_id]["os_vendor"]
        job_id += 1
    
    returns = None


@app.get("/dhcp_info")
def serve_dhcp_server_info():
    global dhcp_server_info
    if not dhcp_server_info or "error" in dhcp_server_info.keys():
        dhcp_server_info = get_dhcp_server_info()

    return dhcp_server_info

@app.get("/request_progress")
def get_current_progress():

    if lb.total_value == 0:
        return {"flag" : False}

    return {"flag" : True, "progress" : lb.counter, "total" : lb.total_value, "label" : lb.label}