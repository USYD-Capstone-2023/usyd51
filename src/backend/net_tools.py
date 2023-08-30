from scapy.all import traceroute, conf, ARP, Ether, srp
import nmap, socket

# Collection of thread workers that run a singular scan (one address) of a given type

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