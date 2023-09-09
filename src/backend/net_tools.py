from scapy.all import traceroute, conf, ARP, Ether, srp, sr1, TCP, IP
import nmap, socket, netifaces, requests

# Collection of tools used to get information from the network and its devices

# Sends an ARP ping to the given ip address
def arp_helper(ip):
    # Creating ARP packet
    arp_frame = ARP(pdst=ip)
    ethernet_frame = Ether(dst="FF:FF:FF:FF:FF:FF")
    request = ethernet_frame / arp_frame

    # Send/recieve packet
    responded = srp(request, timeout=0.3, retry=2, verbose=False)[0]

    ip = None
    mac = None

    if len(responded) > 0:
        ip = responded[0][1].psrc
        mac = responded[0][1].hwsrc

    return ip, mac


# Thread worker to get path to provided ip address
def traceroute_helper(args):

    ip = args[0]
    gateway = args[1]
    # This one seems to have issues, but doesnt give mac res errors
    # answers = srp(IP(dst=ip, ttl=(1, 30), id=RandShort()) / TCP(flags=0x2), verbose=False, timeout=1)[0]

    # Emits TCP packets with incrementing ttl until the target is reached
    answers = traceroute(ip, verbose=False, maxttl=10, iface=conf.iface, dport=[80, 443])[0]
    addrs = [gateway]

    for response_idx in range(1, len(answers)):
        # Dont register if the packet hit the same router again
        if answers[response_idx].answer.src == addrs[-1]:
            break

        addrs.append(answers[response_idx].answer.src)

    # Occurs in cases where there is no found connection and traceroute fails
    if ip not in addrs:
        addrs.append(ip)

    return addrs


# Thread worker to get os info from the provided ip address
def os_helper(ip):

    nm = nmap.PortScanner()
    # Performs scan
    data = nm.scan(ip, arguments="-O")
    data = data["scan"]

    os_info = {"os_type" : "unknown", "os_vendor" : "unknown", "os_family" : "unknown"}

    # Parses output for os info
    if ip in data.keys():
        if "osmatch" in data[ip] and len(data[ip]["osmatch"]) > 0:
            osmatch = data[ip]["osmatch"][0]
            if 'osclass' in osmatch and len(osmatch["osclass"]) > 0:
                osclass = osmatch["osclass"][0]

                os_info["os_type"] = osclass["type"]
                os_info["os_vendor"] = osclass["vendor"]
                os_info["os_family"] = osclass["osfamily"]

    return os_info


# Thread worker for reverse DNS lookup
def hostname_helper(host):
    try:
        return socket.gethostbyaddr(host)[0]
    except:
        return "unknown"


# Gets the gateway, interface, subnet mask and domain name of the current network
def get_dhcp_server_info():

    gws = netifaces.gateways()

    # Failsafe defaults in the event that there is no network connection
    default_gateway = None
    default_iface = "unknown"
    subnet_mask = "255.255.255.0"
    domain = "unknown"

    if "default" in gws.keys() and netifaces.AF_INET in gws["default"].keys():

        default_gateway = netifaces.gateways()["default"][netifaces.AF_INET][0]
        default_iface = netifaces.gateways()["default"][netifaces.AF_INET][1]
        subnet_mask = netifaces.ifaddresses(default_iface)[netifaces.AF_INET][0]["netmask"]
        domain = hostname_helper(default_gateway)

    return {"router" : default_gateway, "iface" : default_iface, "subnet_mask" : subnet_mask, "domain" : domain}

def check_port(ip, port):
    
    try:
        # Create a TCP SYN packet to check if the port is open
        response = sr1(IP(dst=ip) / TCP(dport=port, flags="S"), timeout=1, verbose=False)

        if response and response.haslayer(TCP):
            if response.getlayer(TCP).flags == 0x12:  # TCP SYN-ACK flag
                return True #return True if the port is open
            else:
                return False #return false if the port is closed
        else:
            return False #return false if the port is closed
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def check_website(ip):
    url = f"http://{ip}"  # Construct the URL with the provided IP
    try:
        response = requests.get(url, timeout=1)
        
        # Check if the response status code is in the 200 range (i.e., a successful response)
        if 200 <= response.status_code < 300:
            return True #return true if this hosts a website
        else:
            return False #return false if this does not host a website
    except requests.RequestException as e:
        return False #return false if this does not host a website
    
def in_class_A(ip):
    A_ip_range = [[10, 0, 0, 0], [10, 255, 255, 255]]
    ip = ip.split(".")
    ip = [int(x) for x in ip] 
    if ip[0] == 10:
        return True
    else:
        return False
    
def in_class_B(ip):
    B_ip_range = [[172,16,0,0], [172, 31, 255, 255]]
    ip = ip.split(".")
    ip = [int(x) for x in ip] 
    if ip[0] == 172:
        if ip[1] >= 16 and ip[1] <= 31:
            return True
    return False

def in_class_C(ip):
    C_ip_range = [[192, 168, 0, 0], [192, 168, 255, 255]]
    ip = ip.split(".")
    ip = [int(x) for x in ip] 
    #print(ip)
    if ip[0] == 192:
        #print(196)
        if ip[1] == 168:
            #print(168)
            return True
    return False

def vertical_traceroute(target_host="8.8.8.8"):
    # Define the target host (in this case, Google's DNS server)
    # Create a list to store the traceroute results
    traceroute_results = []

    # Perform the traceroute
    for ttl in range(1, 31):  # Set the maximum TTL to 30
        # Create an ICMP echo request packet with the specified TTL
        packet = IP(dst=target_host, ttl=ttl) / ICMP()

        # Send the packet and receive a reply
        reply = sr1(packet, verbose=False, timeout=1)

        if reply is not None:
            traceroute_results.append(reply.src)

        # Check if we have reached the target host
        if reply and reply.src == target_host:
            break

    local_vertical = []
    # Print the traceroute results
    for i, ip in enumerate(traceroute_results):
        if in_class_A(ip) or in_class_B(ip) or in_class_C(ip):
            local_vertical.append(ip)
    
    #returns a list of ip strings that are inside of your network and a part of a traceroute to google
    return local_vertical


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