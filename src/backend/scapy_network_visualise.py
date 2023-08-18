import scapy.all as scapy
import igraph as ig
import matplotlib.pyplot as plt
import json
import sys
from Client import Client
from MAC_table import MAC_table
import nmap
import platform

# This is a problem as you either have one gateway or the other. 
# Im 1.1 and yall are 0.1

# GATEWAY = "192.168.0.1"
GATEWAY = "192.168.1.1"
GATEWAY_FANGED = GATEWAY.split(".")
MAC_TABLE_FILEPATH = "../cache/oui.csv"

def nm_get_os(nm, ip):

    data = nm.scan(ip, arguments = "-O") #  --host-timeout 10")
    data = data["scan"]

    os_info = {"os_type" : "unknown", "os_vendor" : "unknown", "os_family" : "unknown"}

    if ip in data.keys():
        if "osmatch" in data[ip] and len(data[ip]["osmatch"]) > 0:
            osmatch = data[ip]["osmatch"][0]
            if 'osclass' in osmatch and len(osmatch["osclass"]) > 0:
                osclass = osmatch["osclass"][0]

                os_info["os_type"] = osclass["type"]
                os_info["os_vendor"] = osclass["vendor"]
                os_info["os_family"] = osclass["osfamily"]

    return os_info

def nm_get_hostname(nm, ip):

    data = nm.scan(ip, arguments = "--host-timeout 0.1")
    data = data["scan"]
    hostname = ""
    if ip in data.keys():
        hostname = data[ip]["hostnames"][0]["name"]

    return ip if hostname == "" else hostname


def arp_scan(ip_range, clients, mac_table, nm):

    # Creating arp packet
    arp_frame = scapy.ARP(pdst=ip_range)
    ethernet_frame = scapy.Ether(dst="FF:FF:FF:FF:FF:FF")
    request = ethernet_frame / arp_frame

    print("[INFO] Getting all active devices on network.")
    # Run arp scan to retrieve active ips
    responded = scapy.srp(request, timeout=0.2, retry=2, verbose=False)[0]
    print("[INFO] Found %d devices!" % (len(responded)))
    print("[INFO] Resolving hostnames...")

    # total length of progress bar in chars
    length = 40 
    # "full" value of progress bar
    total_val = len(responded)  

    sys.stdout.write('\r')
    sys.stdout.write("[INFO] Scanned: [%s] %d%%" % (' ' * length, 0))
    sys.stdout.flush()
    counter = 0

    for response in responded:
        
        # Retrieves basic client information and creates Client obj
        ip = response[1].psrc
        name = nm_get_hostname(nm, ip)

        mac = response[1].hwsrc
        vendor = mac_table.find_vendor(mac)

        clients[ip] = Client()
        clients[ip].add_host_info(ip, name, mac, vendor)

        # Update progress bar
        counter += 1

        percent = 100.0 * counter / total_val
        sys.stdout.write('\r')
        progress = int(percent / (100.0 / length))
        sys.stdout.write("[INFO] Scanned: [%s%s] %d%%" % ('-' * progress, ' ' * (length - progress), int(percent)))
        sys.stdout.flush()

    print("\n[INFO] Client scanning complete!")


def get_clients(ip_range, mac_table, nm):

    # Adding this computer to list of clients in the map
    own_ip = scapy.get_if_addr(scapy.conf.iface)
    own_mac = scapy.Ether().src
    own_vendor = mac_table.find_vendor(own_mac)
    own_name = s.gethostname()

    this_client = Client()
    this_client.add_host_info(own_ip, own_name, own_mac, own_vendor)
    this_client.add_os_info("general", "%s %s %s" % (platform.system(), platform.release(), platform.version()), platform.system())

    # Adding gateway to list of clients
    print("[INFO] Getting gateway information.")
    gateway_hostname = nm_get_hostname(nm, GATEWAY)
    gateway_mac = scapy.getmacbyip(GATEWAY)
    if gateway_mac == None:
        gateway_mac = "unknown"
    
    gateway_vendor = mac_table.find_vendor(gateway_mac)

    gateway_client = Client()
    gateway_client.add_host_info(GATEWAY, gateway_hostname, gateway_mac, gateway_vendor)
    clients = {own_ip : this_client, GATEWAY : gateway_client}

    # Scans for all clients on the network
    arp_scan(ip_range, clients, mac_table, nm)

    return clients

def get_os_info(clients, nm):

    print("[INFO] Retrieving OS information from devices")

    # total length of progress bar in chars
    length = 40 
    # "full" value of progress bar
    total_val = len(clients.keys())  

    sys.stdout.write('\r')
    sys.stdout.write("[INFO] Scanned: [%s] %d%%" % (' ' * length, 0))
    sys.stdout.flush()
    counter = 0

    for ip in clients.keys():

        data = nm_get_os(nm, ip)
        clients[ip].add_os_info(data["os_type"], data["os_vendor"], data["os_family"])
        
        # Update progress bar
        counter += 1

        percent = 100.0 * counter / total_val
        sys.stdout.write('\r')
        progress = int(percent / (100.0 / length))
        sys.stdout.write("[INFO] Scanned: [%s%s] %d%%" % ('-' * progress, ' ' * (length - progress), int(percent)))
        sys.stdout.flush()

    print("\n[INFO] Completed OS scan!")


# Gets the ip of all devices on the path from the host to the target ip
def traceroute(ip, clients, nm):

    print("[INFO] Tracing route to %s" % (ip))

    # Runs traceroute.
    # Emits TCP packets with incrementing ttl until the target is reached
    # answers = scapy.srp(scapy.IP(dst=ip, ttl=(1, 30))/scapy.TCP(dport=53, flags="S"), timeout=1, retry=5, verbose=False)[0]
    answers = scapy.traceroute(ip, verbose=False)[0]

    addrs = [GATEWAY]
    prev_resp_ip = GATEWAY

    for response_idx in range(1, len(answers)):

        if answers[response_idx].answer.src == prev_resp_ip:
            break

        resp_ip = answers[response_idx].answer.src

        if resp_ip not in clients.keys():

            resp_name = nm_get_hostname(nm, resp_ip)
            resp_mac = scapy.getmacbyip(resp_ip)
            if resp_mac == None:
                resp_mac = "unknown"
            
            resp_vendor = mac_table.find_vendor(resp_mac)

            clients[resp_ip] = Client()
            clients[resp_ip].add_host_info(resp_ip, resp_name, resp_mac, resp_vendor)

        clients[prev_resp_ip].neighbours.add(clients[resp_ip])
        clients[resp_ip].neighbours.add(clients[prev_resp_ip])
        prev_resp_ip = resp_ip

    clients[prev_resp_ip].neighbours.add(clients[ip])
    clients[ip].neighbours.add(clients[prev_resp_ip])

# Prints network visualisation
def draw_graph(edges, vertices):

    print("[INFO] Graph constructed, initialising visualisation")

    n_vertices = len(vertices)

    graph = ig.Graph(n_vertices, edges)

    graph["title"] = "Network Visualisation"

    # Vertex name is hostname if found, otherwise make it the IP of the node.
    graph.vs["name"] = vertices

    fig, ax = plt.subplots(figsize=(20, 20))
    ig.plot(
        graph,
        mode="mutual",
        target=ax,
        vertex_size=0.001,
        vertex_frame_width=4.0,
        vertex_frame_color='white',
        vertex_label=graph.vs["name"],
        vertex_label_size=7.0,
        vertex_label_dist=1.0,
        edge_color='black',
        edge_width=0.1
    )

    fig.savefig("output.png")
    plt.show()


if __name__ == "__main__":

    mac_table = MAC_table(MAC_TABLE_FILEPATH)
    nm = nmap.PortScanner()
    clients = get_clients(f"{GATEWAY_FANGED[0]}.{GATEWAY_FANGED[1]}.{GATEWAY_FANGED[2]}.{GATEWAY_FANGED[3]}/24", mac_table, nm)

    vertices = []
    edges = set()
    for ip in list(clients.keys()):

        traceroute(ip, clients, nm)

    vertices = [clients[key].hostname for key in clients.keys()]

    gateway_client = clients[GATEWAY]
    layer = [gateway_client]
    visited = set()

    # Generates all edges
    read_layer = True
    while layer:

        if read_layer:
            for client in layer:
                for neighbour in client.neighbours:
                    v1 = min(vertices.index(client.hostname), vertices.index(neighbour.hostname))
                    v2 = max(vertices.index(client.hostname), vertices.index(neighbour.hostname))
                    edges.add((v1, v2))

        read_layer = not read_layer
        next_layer = []

        for client in layer:
            for neighbour in client.neighbours:
                if neighbour not in visited:
                    visited.add(neighbour)
                    next_layer.append(neighbour)

        layer = next_layer

    draw_graph(edges, vertices)

    get_os_info(clients, nm)

    out = {client.ip : client.to_map() for client in clients.values()}
    # for client in clients.values():
        # out[client.ip] = client.to_map()

    with open("clients.json", "w") as outfile:
        json.dump(out, outfile)