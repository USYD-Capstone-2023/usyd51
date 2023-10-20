# External
from scapy.all import (
    traceroute,
    conf,
    ARP,
    DNSRR,
    UDP,
    IP,
    TCP,
    Ether,
    srp1,
    sr1,
    get_if_addr,
    sniff,
    show_interfaces,
    # dev_from_index,
)

import nmap3, netifaces

# Local
from job import Job
from MAC_table import MAC_table
from device import Device
from network import Network

# Stdlib
from platform import system
import socket, threading, subprocess, os
from datetime import datetime

MAC_TABLE_FP = "./oui/oui.csv"

mac_table = MAC_table(MAC_TABLE_FP)

def show_int():
    show_interfaces()
    print(conf.iface)


def init_scan(network_id, iface=conf.iface):

    ts = int(datetime.now().timestamp())


    # Retrieves dhcp server information (router ip, subnet mask, domain name)
    dhcp_server_info = get_dhcp_server_info()
    gateway = dhcp_server_info["router"]
    domain = dhcp_server_info["domain"]

    # Wireguard tunnel
    # show_interfaces()
    # iface = dev_from_index(63) # you need to get this index for ur interface list

    gateway_mac = arp_helper(gateway, iface)[1]
    ssid = get_ssid(iface)

    # Creates a network with default name = ssid
    network = Network(ssid, ssid, ts, dhcp_server_info, gateway_mac, network_id)

    # DNS_sniffer = threading.Thread(target=self.run_wlan_sniffer, args=(iface,))
    # DNS_sniffer.daemon = True
    # DNS_sniffer.start()

    client_device = Device(get_if_addr(iface), Ether().src)
    client_device.hostname = socket.gethostname()
    client_device.parent = gateway
    network.add_device(client_device)

    # Creates device object to represent the gateway if one doesnt exist already
    gateway_device = Device(gateway, gateway_mac)
    gateway_device.hostname = domain
    network.add_device(gateway_device)

    return network



# --------------------------------------------- SSID ------------------------------------------ #

def get_ssid(iface=conf.iface):

    current_system = system()

    # MacOS - Get by running the airport program.
    if current_system == "Darwin":

        process = subprocess.Popen(
            [
                "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport",
                "-I",
            ],
            stdout=subprocess.PIPE,
        )
        out, err = process.communicate()
        process.wait()
        for line in out.decode("utf8").split("\n"):
            if " SSID" in line:
                return line.split(": ")[1]

    elif current_system == "Linux":

        return os.popen("iwconfig " + iface + " | grep ESSID | awk '{print $4}' | sed 's/" + '"' + "//g' | sed 's/.*ESSID://'").read()[:-1]

    elif current_system == "Windows":
        out = os.popen('netsh wlan show interfaces | findstr /c:" SSID"').read()[:-1]
        ssid = out.split(":")[-1][1:]

        if len(ssid) == 0:
            out = os.popen('netsh lan show interfaces | findstr /c:" SSID"').read()[:-1]
            ssid = out.split(":")[-1][1:]

        if len(ssid) == 0:
            return "new network"
        
        return ssid

    return "OS UNSUPPORTED"

# ---------------------------------------------- MAC VENDOR ---------------------------------------------- #

# Updates the mac vendor field of all devices in the current network's table of the database
def add_mac_vendors(network, lb):

    # Set loading bar
    lb.set_params("mac_vendor", 40, len(network.devices.keys()))
    lb.show()

    # Adds mac vendor to device and saves to database
    for device in network.devices.values():
        device.mac_vendor = mac_table.find_vendor(device.mac)
        lb.increment()
        lb.show()

    lb.reset()

# ---------------------------------------------- ARP SCANNING ---------------------------------------------- #

# Sends an ARP ping to the given ip address to check it is alive and retrieve its MAC
def arp_helper(ip, iface):

    # Creating ARP packet
    arp_frame = ARP(pdst=ip)
    ethernet_frame = Ether(dst="FF:FF:FF:FF:FF:FF")
    request = ethernet_frame / arp_frame

    # Send/recieve packet
    response = srp1(request, iface=iface, timeout=0.5, retry=2, verbose=False)

    # Formulate return values
    found_ip = None
    found_mac = None

    if response:
        found_ip = response[0][1].psrc
        found_mac = response[0][1].hwsrc

    return found_ip, found_mac


# Gets all active active devices on the network
def add_devices(network, tp, lb, iface=conf.iface):

    print("[INFO] Getting all active devices on network.")

    # Breaks subnet and gateway ip into bytes
    sm_split = network.dhcp_server_info["subnet_mask"].split(".")
    gateway_split = network.dhcp_server_info["router"].split(".")
    first_ip = [0] * 4
    last_ip = [0] * 4

    # Calculates first and last IPs byte by byte, based off subnet mask and router IP
    for i in range(4):
        sm_chunk = int(sm_split[i])
        gateway_chunk = int(gateway_split[i])

        first_ip[i] = sm_chunk & gateway_chunk
        sm_inv = (1 << 8) - 1 - sm_chunk
        last_ip[i] = sm_inv | (sm_chunk & gateway_chunk)

    # Generates return array of size equal to the number of IPs in the range
    num_addrs = 1
    for i in range(4):
        num_addrs *= max(last_ip[i] - first_ip[i] + 1, 1)

    returns = [-1] * num_addrs

    # Set loading bar
    lb.set_params("get_devices", 40, num_addrs)
    lb.show()

    # Preparing thread job parameters
    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]

    # The current job, for referencing the return location for the thread
    job_counter = 0

    # Iterates over full IP range
    for p1 in range(first_ip[0], last_ip[0] + 1):
        for p2 in range(first_ip[1], last_ip[1] + 1):
            for p3 in range(first_ip[2], last_ip[2] + 1):
                for p4 in range(first_ip[3], last_ip[3] + 1):
                    # Creates job and adds to threadpool queue for execution
                    ip = "%d.%d.%d.%d" % (p1, p2, p3, p4)
                    job = Job(
                        fptr=arp_helper,
                        args=(ip, iface,),
                        ret_ls=returns,
                        ret_id=job_counter,
                        counter_ptr=counter_ptr,
                        cond=cond,
                    )
                    job_counter += 1

                    if not tp.add_job(job):
                        return "Request size over maximum allowed size %d" % (tp.MAX_QUEUE_SIZE)

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
        if mac and ip and mac not in network.devices.keys():
            network.devices[mac] = Device(ip, mac)

    print("[INFO] Found %d devices!" % (len(network.devices)))
    lb.reset()

# ---------------------------------------------- TRACEROUTE ---------------------------------------------- #

# Thread worker to get path to provided ip address
def traceroute_helper(ip, gateway, iface):

    # Emits UDP packets with incrementing ttl until the target is reached
    answers = traceroute(ip, maxttl=10, iface=iface, verbose=False)[0]
    addrs = [gateway]

    # Responses return out of order so we reorder them by ttl
    hops = {}
    if ip in answers.get_trace().keys():
        for answer in answers.get_trace()[ip].keys():
            hops[answer] = answers.get_trace()[ip][answer][0]

    for hop in sorted(hops.keys()):
        if hops[hop] not in addrs:
            addrs.append(hops[hop])

    if addrs[-1] != ip:
        addrs.append(ip)

    return addrs


# Runs a traceroute on all devices in the database to get their neighbours in the routing path, updates and saves to database
def add_routes(network, tp, lb, iface=conf.iface):

    print("[INFO] Tracing Routes...")

    # Retrieve network devices from database
    device_addrs = set()
    gateway = network.dhcp_server_info["router"]

    # Set loading bar
    lb.set_params("traceroute", 40, len(network.devices.keys()))
    lb.show()

    # Preparing thread job parameters
    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]
    returns = [-1] * len(network.devices.keys())

    # The current job, for referencing the return location for the thread
    job_counter = 0

    for device in network.devices.values():
        # Creates job and adds to threadpool queue for execution
        device_addrs.add(device.ip)
        job = Job(
            fptr=traceroute_helper,
            args=(device.ip, gateway, iface,),
            ret_ls=returns,
            ret_id=job_counter,
            counter_ptr=counter_ptr,
            cond=cond,
        )
        job_counter += 1

        if not tp.add_job(job):
            return "Request size over maximum allowed size %d" % (
                tp.MAX_QUEUE_SIZE
            )

    # Waits for all jobs to be completed by the threadpool
    mutex.acquire()
    while counter_ptr[0] < len(network.devices.keys()):
        cond.wait()
        lb.set_progress(counter_ptr[0])
        lb.show()

    mutex.release()
    print("[INFO] Traceroute complete!")

    to_add = []
    # Parses output
    job_counter = 0
    for device in network.devices.values():
        parent = gateway
        for addr in returns[job_counter]:
            # Adds devices if they don't already exist
            if addr not in device_addrs:
                device_addrs.add(addr)
                mac = arp_helper(addr, iface)[1]
                new_device = Device(addr, mac)
                new_device.parent = parent
                to_add.append(new_device)

            if addr == device.ip:
                break

            parent = addr

        # Updates the devices parent node
        device.parent = parent
        job_counter += 1

    for device in to_add:
        network.devices[device.mac] = device

    lb.reset()


# def check_website(ip):

#     url = f"http://{ip}"  # Construct the URL with the provided IP
#     try:
#         response = requests.get(url, timeout=1)
        
#         # Check if the response status code is in the 200 range (i.e., a successful response)
#         if 200 <= response.status_code < 300:
#             return True #return true if this hosts a website
#         else:
#             return False #return false if this does not host a website
#     except requests.RequestException as e:
#         return False #return false if this does not host a website
    

def vertical_traceroute(network, iface=conf.iface, target_host="8.8.8.8"):

    # Run traceroute to google's DNS server
    traceroute_results = traceroute_helper(target_host, network.dhcp_server_info["router"], iface)
    # Print the traceroute results
    for i in range(len(traceroute_results) - 1):
        ip = traceroute_results[i]
        if get_ip_class(ip) != None:

            mac = arp_helper(ip, iface)[1]
            if mac == None:
                continue

            if mac in network.devices.keys():
                network.devices[mac].parent = traceroute_results[i+1]
                continue

            new_device = Device(ip, mac)
            new_device.parent = traceroute_results[i+1]
            network.devices[mac] = new_device


# ---------------------------------------------- OS FINGERPRINTING ---------------------------------------------- #

# Thread worker to get os info from the provided ip address
def os_helper(ip):

    nm = nmap3.Nmap()
    # Performs scan
    data = nm.nmap_os_detection(ip, args="--script-timeout 20")

    os_info = {"os_type": "unknown", "os_vendor": "unknown", "os_family": "unknown"}

    # Parses output for os info
    if ip in data.keys():
        if "osmatch" in data[ip] and len(data[ip]["osmatch"]) > 0:
            osmatch = data[ip]["osmatch"][0]
            if "osclass" in osmatch:
                osclass = osmatch["osclass"]

                os_info["os_type"] = osclass["type"]
                os_info["os_vendor"] = osclass["vendor"]
                os_info["os_family"] = osclass["osfamily"]

    return os_info


def add_os_info(network, tp, lb, iface=conf.iface):

    print("[INFO] Getting OS info...")

    # Set loading bar
    lb.set_params("os_scan", 40, len(network.devices.keys()))
    lb.show()

    # Preparing thread job parameters
    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]
    returns = [-1] * len(network.devices.keys())

    # The current job, for referencing the return location for the thread
    job_counter = 0
    for device in network.devices.values():
        # Create job and add to threadpool queue for execution
        job = Job(
            fptr=os_helper,
            args=(device.ip,),
            ret_ls=returns,
            ret_id=job_counter,
            counter_ptr=counter_ptr,
            cond=cond,
        )
        job_counter += 1

        if not tp.add_job(job):
            return "Request size over maximum allowed size %d" % (
                tp.MAX_QUEUE_SIZE
            )

    # Waits for all jobs to be completed
    mutex.acquire()
    while counter_ptr[0] < len(network.devices.keys()):
        cond.wait()
        lb.set_progress(counter_ptr[0])
        lb.show()

    mutex.release()

    # Sets all devices OS information
    job_id = 0
    for device in network.devices.values():
        device.os_type = returns[job_id]["os_type"]
        device.os_family = returns[job_id]["os_family"]
        device.os_vendor = returns[job_id]["os_vendor"]
        job_id += 1

    print("[INFO] OS scan complete!")

    # Reset loading bar for next task. Enables frontend to know job is complete.
    lb.reset()

# ---------------------------------------------- HOSTNAME LOOKUP ---------------------------------------------- #

# Thread worker for reverse DNS lookup
def hostname_helper(addr):

    try:
        return socket.gethostbyaddr(addr)[0]
    except:
        return "unknown"


# Retrieves the hostnames of all devices on the network and saves them to the database
def add_hostnames(network, tp, lb):

    # Set loading bar
    lb.set_params("hostnames", 40, len(network.devices.keys()))
    lb.show()

    # Preparing thread job parameters
    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]
    returns = [-1] * len(network.devices.keys())

    # The current job, for referencing the return location for the thread
    job_counter = 0

    for device in network.devices.values():

        # Create job and add to threadpool queue for execution
        job = Job(
            fptr=hostname_helper,
            args=(device.ip,),
            ret_ls=returns,
            ret_id=job_counter,
            counter_ptr=counter_ptr,
            cond=cond,
        )
        job_counter += 1

        if not tp.add_job(job):
            return "Request size over maximum allowed size %d" % (tp.MAX_QUEUE_SIZE)

    # Wait for all jobs to be comleted
    mutex.acquire()
    while counter_ptr[0] < len(network.devices.keys()):
        cond.wait()
        lb.set_progress(counter_ptr[0])
        lb.show()

    mutex.release()

    # Add returned hostnames to devices, save to database
    job_counter = 0
    for device in network.devices.values():
        if returns[job_counter] != "unkown":
            device.hostname = returns[job_counter]
        job_counter += 1

    print("[INFO] Name resolution complete!")

    # Reset loading bar for next task. Enables frontend to know job is complete.
    lb.reset()

# ---------------------------------------------- DHCP INFO ---------------------------------------------- #

# Gets the gateway, interface, subnet mask and domain name of the current network
def get_dhcp_server_info():

    print("[INFO] Retrieving DHCP server info...")

    gws = netifaces.gateways()

    # Failsafe defaults in the event that there is no network connection
    default_gateway = None
    default_iface = "unknown"
    subnet_mask = "255.255.255.0"
    domain = "unknown"

    if "default" in gws.keys() and netifaces.AF_INET in gws["default"].keys():
        default_gateway = netifaces.gateways()["default"][netifaces.AF_INET][0]
        default_iface = netifaces.gateways()["default"][netifaces.AF_INET][1]
        subnet_mask = netifaces.ifaddresses(default_iface)[netifaces.AF_INET][0][
            "netmask"
        ]
        domain = hostname_helper(default_gateway)

    return {
        "router": default_gateway,
        "iface": default_iface,
        "subnet_mask": subnet_mask,
        "domain": domain,
    }


def get_gateway_mac(iface=conf.iface):

    dhcp_info = get_dhcp_server_info()
    return arp_helper(dhcp_info["router"], iface)[1]

# ---------------------------------------------- DNS SNIFFER ---------------------------------------------- #

# # Packet sniffing daemon to get hostnames
# def wlan_sniffer_callback(self, pkt):

#     # Sniffs mDNS responses for new hostnames and devices
#     if IP in pkt and UDP in pkt and pkt[UDP].dport == 5353:
#         # Can only be saved to database if the network is registered
#         if not self.db.contains_network(self.network_id):
#             return

#         ip = pkt[IP].src
#         mac = arp_helper(ip, iface)[1]

#         if mac == None:
#             return

#         # Add device to database if it doesnt exist
#         if not self.db.contains_mac(self.network_id, mac, self.ts):
#             device = Device(ip, mac)
#             device.mac_vendor = self.mac_table.find_vendor(mac)
#             device.parent = traceroute_helper(ip, self.gateway, self.iface)[-1]
#             self.db.add_device(self.network_id, device, self.ts)

#         if DNSRR in pkt:
#             # Exclude non-human names and addresses
#             name = pkt[DNSRR].rrname.decode("utf-8")
#             if name.split(".")[-2] != "arpa" and name[0] != "_":
#                 # Update existing device and save to database if it already exists
#                 device = self.db.get_device(self.network_id, mac, self.ts)
#                 if device == None:
#                     print("[DEBUG] err in wlan sniff")
#                     return

#                 if device.hostname == "unknown":
#                     device.hostname = name
#                     self.db.save_device(self.network_id, device, self.ts)


# def run_wlan_sniffer(self, iface, args):
#     sniff(prn=wlan_sniffer_callback, iface=iface, args=args)

# ---------------------------------------- IP ----------------------------------------------------- #
        
def get_ip_class(ip):

    def ip_val(ip):

        val = 0
        exp = 0

        for i in ip.split(".")[::-1]:
            val += int(i) * pow(256, exp)
            exp += 1
        return val
    
    ip = ip_val(ip)

    if ip >= ip_val("10.0.0.0") and ip <= ip_val("10.255.255.255"):
        return "A"
    
    if ip >= ip_val("172.16.0.0") and ip <= ip_val("172.31.255.255"):
        return "B"

    if ip >= ip_val("192.168.0.0") and ip <= ip_val("192.168.255.255"):
        return "C"
    
    return None

# ---------------------------------------- PORTS ---------------------------------------------------- #

def ports_helper(ip, iface, ports):

    out = [False] * len(ports)
    idx = 0

    for port in ports:
        try:
            # Create a TCP SYN packet to check if the port is open
            response = sr1(IP(dst=ip) / TCP(dport=port, flags="S"), timeout=1, iface=iface, verbose=False)

            if response and response.haslayer(TCP):
                # TCP SYN-ACK flag
                if response.getlayer(TCP).flags == 0x12:  
                    #return True if the port is open
                    out[idx] = True
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        idx += 1
    return out


def add_ports(network, tp, lb, ports, iface=conf.iface):

    if ports == []:
        return
    
    # Set loading bar
    lb.set_params("ports", 40, len(network.devices.keys()))
    lb.show()

    # Preparing thread job parameters
    mutex = threading.Lock()
    cond = threading.Condition(lock=mutex)
    counter_ptr = [0]
    returns = [-1] * len(network.devices.keys())

    # The current job, for referencing the return location for the thread
    job_counter = 0

    for device in network.devices.values():

        # Create job and add to threadpool queue for execution
        job = Job(
            fptr=ports_helper,
            args=(device.ip, iface, ports,),
            ret_ls=returns,
            ret_id=job_counter,
            counter_ptr=counter_ptr,
            cond=cond,
        )
        job_counter += 1

        if not tp.add_job(job):
            return "Request size over maximum allowed size %d" % (tp.MAX_QUEUE_SIZE)

    # Wait for all jobs to be comleted
    mutex.acquire()
    while counter_ptr[0] < len(network.devices.keys()):
        cond.wait()
        lb.set_progress(counter_ptr[0])
        lb.show()

    mutex.release()

    # Add returned hostnames to devices, save to database
    job_counter = 0
    for device in network.devices.values():
        ports_open = []
        for port_idx in range(len(returns[job_counter])):
            if returns[job_counter][port_idx]:
                ports_open.append(ports[port_idx])

        device.ports = ports_open
        job_counter += 1

# Active DNS, LLMNR, MDNS requests, cant get these to work at the minute but theyll be useful
# ---------------------------------------- WIP -----------------------------------------

# iface = self.iface

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
