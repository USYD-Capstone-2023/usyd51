from flask import Flask
from MAC_table import MAC_table
from Loading_bar import Loading_bar
from scapy.all import *
import nmap, os, socket, platform
import time, threading

MAC_TABLE_FP = "../cache/oui.csv"

# Ensures that the user has root perms uf run on posix system.
if os.name == "posix" and os.geteuid() != 0: 
    print("Root permissions are required for this program to run.")
    quit()

mac_table = MAC_table()
own_ip = get_if_addr(conf.iface)
own_mac = Ether().src
own_name = platform.node()
app = Flask(__name__)
wifi = {"bssid" : [], "ssid" : []}

def wifi_sniffer_callback(pkt):

    print("wowowow")
    if pkt.haslayer(Dot11Beacon):
        if pkt.addr2 not in wifi["bssid"]:

            wifi["bssid"].append(pkt.addr2)
            wifi["ssid"].append(pkt.info)

def temp_info_thread():
    while True:
        # os.system("clear")
        print(wifi)
        print("\n")
        time.sleep(0.5)

@app.get("/network_info")
def get_network_info():

    iface = conf.iface
    info_thread = threading.Thread(target=temp_info_thread)
    info_thread.daemon = True
    info_thread.start()
    sniff(prn=wifi_sniffer_callback, iface=iface)


# Returns the vendor associated with each ip provided in "macs"
@app.get("/mac_vendor/<macs>")
def get_mac_vendor(macs):
    if not mac_table.initialized:
        mac_table.init_mac_table(MAC_TABLE_FP)

    ret = {}
    macs = macs.split(",")
    lb = Loading_bar("Resolving Hostnames", 40, len(macs))

    for mac in macs:
        ret[mac] = mac_table.find_vendor(mac)
        lb.increment()

    return ret

# Performs a reverse DNS lookup on all hosts entered in "hosts"
@app.get("/hostname/<hosts>")
def get_hostnames(hosts):

    ret = {}
    hosts = hosts.split(",")
    lb = Loading_bar("Resolving Hostnames", 40, len(hosts))
    for host in hosts:

        if host == own_ip:
            ret[host] = own_name
            continue

        hostname = host
        try:
            hostname = socket.gethostbyaddr(host)[0]
        except:
            pass

        ret[host] = hostname
        lb.increment()

    return ret

# Gets the IP and MAC of all devices currently active on the network 
@app.get("/devices")
def get_devices():

    # Creating ARP packet
    arp_frame = ARP(pdst="192.168.1.0/24")
    ethernet_frame = Ether(dst="FF:FF:FF:FF:FF:FF")
    request = ethernet_frame / arp_frame

    print("[INFO] Getting all active devices on network.")
    # Run ARP scan to retrieve active IPs
    responded = srp(request, timeout=2, retry=3, verbose=False)[0]
    print("[INFO] Found %d devices!\n" % (len(responded)))

    ret = {}
    for response in responded:
        
        ip = response[1].psrc
        mac = response[1].hwsrc
        ret[ip] = mac

    if own_ip not in ret.keys():
        ret[own_ip] = own_mac

    return ret

# Gets the OS information of the given ip address through TCP fingerprinting
def os_scan(nm, addr):

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

# Retrieves the OS information of all devices corresponding to IPs entered in "addrs" 
@app.get("/os_info/<addrs>")
def get_os_info(addrs):

    addrs = addrs.split(",")
    ret = {}

    print("[INFO] Retrieving OS information from devices")

    lb = Loading_bar("Scanning", 40, len(addrs))
    nm = nmap.PortScanner()

    for addr in addrs:

        data = os_scan(nm, addr)
        ret[addr] = {"os_type" : data["os_type"], "os_vendor" : data["os_vendor"], "os_family" : data["os_family"]}
        lb.increment()

    print("\n[INFO] Completed OS scan!\n")

    return ret