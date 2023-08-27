# External
from flask import Flask
from scapy.all import *
import nmap, socket, platform

# Local
from MAC_table import MAC_table
from loading_bar import Loading_bar
from job import Job
from threadpool import Threadpool
from DHCP_info import get_dhcp_server_info

# Stdlib
import time, threading, socket, os, signal, sys

MAC_TABLE_FP = "../cache/oui.csv"
NUM_THREADS = 25

# Ensures that the user has root perms uf run on posix system.
if os.name == "posix" and os.geteuid() != 0: 
    print("Root permissions are required for this program to run.")
    quit()

mac_table = MAC_table(MAC_TABLE_FP)
own_ip = get_if_addr(conf.iface)
own_mac = Ether().src
own_name = platform.node()
app = Flask(__name__)
devices = {}

lb = Loading_bar()

# Default value, gets resolved on initialization by DHCP server
gateway = "192.168.1.1"
print("[INFO] Retrieveing DHCP server info...")
dhcp_server_info = get_dhcp_server_info()
if "error" not in dhcp_server_info.keys() and len(dhcp_server_info.keys()) > 1:
    gateway = dhcp_server_info["server_id"]

threadpool = Threadpool(NUM_THREADS)

def cleanup(*args,):
    threadpool.end()
    print("Finished cleaning up! Server will now shut down.")
    sys.exit()

signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

def init():

    # Seems to only work on some networks, potentially a proxy or firewall issue.
    # ---------------------------------------- WIP -----------------------------------------
    # packet sniffing daemon to get hostnames
    def wlan_sniffer_callback(pkt):

        # Sniffs mDNS responses for new hostnames
        if IP in pkt and UDP in pkt and pkt[UDP].dport == 5353:
            if pkt[IP].src in devices.keys():
                return

            if DNSRR in pkt:
                name = pkt[DNSRR].rrname.decode("utf-8")
                if name.split(".")[-2] != "arpa" and name[0] != "_":
                    devices[pkt[IP].src] = name.split(".")[0]


    def start_sniff_thread(iface):
        sniff(prn=wlan_sniffer_callback, iface=iface)

    # ---------------------------------------- WIP -----------------------------------------
    channel_switch = threading.Thread(target=start_sniff_thread, args=(conf.iface,))
    channel_switch.daemon = True
    channel_switch.start()

init()


# Returns the vendor associated with each ip provided in "macs"
# Runs in single thread as it is O(n)
@app.get("/mac_vendor/<macs>")
def get_mac_vendor(macs):

    ret = {}
    macs = macs.split(",")
    lb.set_params("Resolving Hostnames", 40, len(macs))
    lb.show()

    for mac in macs:
        ret[mac] = mac_table.find_vendor(mac)
        lb.increment()
        lb.show()

    lb.set_params("", 0, 0)
    return ret


# Performs a reverse DNS lookup on all hosts entered in "hosts"
@app.get("/hostname/<hosts>")
def get_hostnames(hosts):

    # Thread task for reverse DNS lookup
    def hostname_helper(host):
        try:
            return socket.gethostbyaddr(host)[0]
        except:
            return "unknown"


    hosts = hosts.split(",")
    returns = [-1] * len(hosts)
    
    lb.set_params("Resolving Hostnames", 40, len(hosts))
    lb.show()

    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]
    dispatched = len(hosts)

    for i in range(len(hosts)):

        # If hostname has been found in wlan DNSRR sniffer use it instead
        if hosts[i] in devices.keys():
            lb.increment()
            dispatched -= 1
            returns[i] = devices[hosts[i]]
            continue

        if not threadpool.add_job(Job(fptr=hostname_helper, args=hosts[i], ret_ls=returns,\
                                ret_id=i, counter_ptr=counter_ptr, cond=cond)):
                                
            return "Request size over maximum allowed size %d" % (threadpool.MAX_QUEUE_SIZE)

    threadpool.start()

    mutex.acquire()
    while counter_ptr[0] < dispatched:
        cond.wait()
        lb.set_progress(counter_ptr[0] + (len(hosts) - dispatched))
        lb.show()
    mutex.release()

    ret = {}
    for i in range(len(hosts)):
        if returns[i] != "unknown" and hosts[i] not in devices.keys():
            devices[hosts[i]] = returns[i]

        ret[hosts[i]] = returns[i]
    
    threadpool.stop()

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
    lb.set_params("", 0, 0)
    return ret

@app.get("/traceroute/<hosts>")
def get_traceroute(hosts):

    # Thread task to get path to "host"
    def traceroute_helper(host):
        # This one seems to have issues, but doesnt give mac res errors
        # answers = srp(IP(dst=host, ttl=(1, 30), id=RandShort()) / TCP(flags=0x2), verbose=False, timeout=1)[0]

        # Emits TCP packets with incrementing ttl until the target is reached
        answers = traceroute(host, verbose=False)[0]
        addrs = [gateway]

        for response_idx in range(1, len(answers)):
            # Dont register if the packet hit the same router again
            if answers[response_idx].answer.src == addrs[-1]:
                break

            addrs.append(answers[response_idx].answer.src)

        # Occurs in cases where there is no found connection and traceroute fails
        if host not in addrs:
            addrs.append(host)

        return addrs
        

    print("[INFO] Tracing Routes...")

    hosts = hosts.split(",")
    returns = [-1] * len(hosts)
    
    lb.set_params("Tracing routes to devices", 40, len(hosts))
    lb.show()
    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]

    for i in range(len(hosts)):
        if not threadpool.add_job(Job(fptr=traceroute_helper, args=hosts[i], ret_ls=returns,\
                               ret_id=i, counter_ptr=counter_ptr, cond=cond)):

            returns = None
            return "Request size over maximum allowed size %d" % (threadpool.MAX_QUEUE_SIZE)

    threadpool.start()

    mutex.acquire()
    while counter_ptr[0] < len(hosts):
        cond.wait()
        lb.set_progress(counter_ptr[0])
        lb.show()

    mutex.release()
    threadpool.stop()
    print("\n[INFO] Traceroute complete!\n")

    ret = {}
    for i in range(len(hosts)):
        ret[hosts[i]] = returns[i]
    
    returns = None
    lb.set_params("", 0, 0)
    return ret


# Gets the IP and MAC of all devices currently active on the network 
@app.get("/devices")
def get_devices():

    # Sends an ARP ping to the given IP address
    def arp_helper(ip):
        # Creating ARP packet
        arp_frame = ARP(pdst=ip)
        ethernet_frame = Ether(dst="FF:FF:FF:FF:FF:FF")
        request = ethernet_frame / arp_frame

        # Send/recieve packet
        responded = srp(request, timeout=0.3, retry=2, verbose=False)[0]

        ret = {}
        for response in responded:
        
            ip = response[1].psrc
            mac = response[1].hwsrc
            ret[ip] = mac

        return ret


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
                    if not threadpool.add_job(Job(fptr=arp_helper, args=ip, ret_ls=returns,\
                                            ret_id=id, counter_ptr=counter_ptr, cond=cond)):

                        returns = None
                        return "Request size over maximum allowed size %d" % (threadpool.MAX_QUEUE_SIZE)
                    
                    id += 1

    threadpool.start()

    mutex.acquire()
    while counter_ptr[0] < num_addrs:
        cond.wait()
        lb.set_progress(counter_ptr[0])
        lb.show()

    mutex.release()
    threadpool.stop()

    ret = {}
    for i in range(num_addrs):
        for key in returns[i].keys():
            ret[key] = returns[i][key]

    print("\n[INFO] Found %d devices!\n" % (len(ret.keys())))
    returns = None
    lb.set_params("", 0, 0)
    return ret


# Gets the OS information of the given ip address through TCP fingerprinting
@app.get("/os_info/<hosts>")
def os_scan(hosts):

    nm = nmap.PortScanner()

    # Thread worker to get os info from the provided ip address
    def os_helper(addr):

        # Performs scan
        data = nm.scan(addr, arguments="-O")
        data = data["scan"]

        os_info = {"os_type" : "unknown", "os_vendor" : "unknown", "os_family" : "unknown"}

        # Parses output for os info
        if addr in data.keys():
            if "osmatch" in data[addr] and len(data[addr]["osmatch"]) > 0:
                osmatch = data[addr]["osmatch"][0]
                if 'osclass' in osmatch and len(osmatch["osclass"]) > 0:
                    osclass = osmatch["osclass"][0]

                    os_info["os_type"] = osclass["type"]
                    os_info["os_vendor"] = osclass["vendor"]
                    os_info["os_family"] = osclass["osfamily"]

        return os_info


    print("[INFO] Getting OS info...")

    hosts = hosts.split(",")
    returns = [-1] * len(hosts)
    
    lb.set_params("Scanned", 40, len(hosts))
    lb.show()

    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]

    for i in range(len(hosts)):
        if not threadpool.add_job(Job(fptr=os_helper, args=hosts[i], ret_ls=returns,\
                               ret_id=i, counter_ptr=counter_ptr, cond=cond)):

            returns = None
            return "Request size over maximum allowed size %d" % (threadpool.MAX_QUEUE_SIZE)

    threadpool.start()

    mutex.acquire()
    while counter_ptr[0] < len(hosts):
        cond.wait()
        lb.set_progress(counter_ptr[0])
        lb.show()

    mutex.release()
    threadpool.stop()
    print("\n[INFO] OS scan complete!\n")

    ret = {}
    for i in range(len(hosts)):
        ret[hosts[i]] = returns[i]
    
    returns = None
    lb.set_params("", 0, 0)
    return ret


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