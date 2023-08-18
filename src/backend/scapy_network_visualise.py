import scapy.all as scapy
import igraph as ig
import matplotlib.pyplot as plt
import json
from Client import Client
from MAC_table import MAC_table
from Loading_bar import Loading_bar
import nmap
import platform
import os
import sys

# This is a problem as you either have one gateway or the other. 
# Im 1.1 and yall are 0.1

# GATEWAY = "192.168.0.1"
GATEWAY = "192.168.1.1"
GATEWAY_FANGED = GATEWAY.split(".")
MAC_TABLE_FILEPATH = "../cache/oui.csv"


# Retrieves os information of a device by approximation using TCP/IP stack fingerprinting
# TODO - parallelise as much as possible. This is easily the slowest process in the entire program
def nm_get_os(nm, ip):

    data = nm.scan(ip, arguments="-O", sudo=True)
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


# Performs a reverse DNS lookup
# TODO - parallelise as much as possible. Check timeout limits, unsure how fast dns is resolved but seems to work on my network
def nm_get_hostname(nm, ip):

    data = nm.scan(ip, arguments="--host-timeout 0.5", sudo=True)
    data = data["scan"]
    hostname = ""
    if ip in data.keys():
        hostname = data[ip]["hostnames"][0]["name"]

    return ip if hostname == "" else hostname


# Scans for all active ips (and MACs) on the network and converts them into Client objects
# TODO - set ip range based on subnet mask not just GATEWAY/24
def arp_scan(ip_range, clients, mac_table, nm):

    # Creating arp packet
    arp_frame = scapy.ARP(pdst=ip_range)
    ethernet_frame = scapy.Ether(dst="FF:FF:FF:FF:FF:FF")
    request = ethernet_frame / arp_frame

    print("[INFO] Getting all active devices on network.")
    # Run arp scan to retrieve active ips
    responded = scapy.srp(request, timeout=1, retry=4, verbose=False)[0]
    print("[INFO] Found %d devices!\n" % (len(responded)))
    print("[INFO] Resolving hostnames...")

    lb = Loading_bar("Resolved", 40, len(responded))

    for response in responded:
        
        # Retrieves basic client information and creates Client obj
        ip = response[1].psrc
        name = nm_get_hostname(nm, ip)

        mac = response[1].hwsrc
        vendor = mac_table.find_vendor(mac)

        clients[ip] = Client()
        clients[ip].add_host_info(ip, name, mac, vendor)

        lb.increment()

    print("\n[INFO] Hostname resolution complete!\n")


# Creates a Client object for all connected clients on the network, including the current computer and gateway
def get_clients(ip_range, mac_table, nm):

    # Adding this computer to list of clients in the map
    own_ip = scapy.get_if_addr(scapy.conf.iface)
    own_mac = scapy.Ether().src
    own_vendor = mac_table.find_vendor(own_mac)
    own_name = platform.node()

    this_client = Client()
    this_client.add_host_info(own_ip, own_name, own_mac, own_vendor)
    this_client.add_os_info("general", "%s %s %s" % (platform.system(), platform.release(), platform.version()), platform.system())

    # Adding gateway to list of clients
    print("\n[INFO] Getting gateway information.")
    gateway_hostname = nm_get_hostname(nm, GATEWAY)
    gateway_mac = scapy.getmacbyip(GATEWAY)
    if gateway_mac == None:
        gateway_mac = "unknown"
    
    gateway_vendor = mac_table.find_vendor(gateway_mac)

    gateway_client = Client()
    gateway_client.add_host_info(GATEWAY, gateway_hostname, gateway_mac, gateway_vendor)
    clients = {own_ip : this_client, GATEWAY : gateway_client}

    # Gets all other clients on the network
    arp_scan(ip_range, clients, mac_table, nm)

    return clients

# Retrieves the OS info of all known clients on the network 
def get_os_info(clients, nm):

    print("[INFO] Retrieving OS information from devices")

    lb = Loading_bar("Scanned", 40, len(clients.keys()))

    for ip in clients.keys():

        data = nm_get_os(nm, ip)
        clients[ip].add_os_info(data["os_type"], data["os_vendor"], data["os_family"])
        
        lb.increment()

    print("\n[INFO] Completed OS scan!\n")


# Gets the ip of all devices on the path from the host to every ip on the LAN
# TODO - Parallelise this if possible
def map_network(clients, nm):

    print("[INFO] Mapping network...")
    lb = Loading_bar("Mapped", 40, len(clients.keys()))

    for ip in clients.keys():

        # Emits TCP packets with incrementing ttl until the target is reached
        answers = scapy.srp(scapy.IP(dst=ip, ttl=(1, 30), id=scapy.RandShort())/scapy.TCP(flags=0x2), verbose=False, timeout=1)[0]

        addrs = [GATEWAY]
        prev_resp_ip = GATEWAY

        for response_idx in range(1, len(answers)):

            # Dont register if the packet hit the same router again
            if answers[response_idx].answer.src == prev_resp_ip:
                break

            resp_ip = answers[response_idx].answer.src

            # Create a new Client object if the ip is not registered
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

        lb.increment()
    print("\n[INFO] Mapping complete!\n")

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


# Converts the client map into a tuple of vertices and edges
def get_graph_components(clients):

    vertices = [clients[key].hostname for key in clients.keys()]
    edges = set()

    gateway_client = clients[GATEWAY]
    layer = [gateway_client]
    visited = set()

    # Performs a BFS from the gateway, taking the neighbours of every client in every second layer
    # as edges
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
    
    return edges, vertices

if __name__ == "__main__":

    mac_table = MAC_table(MAC_TABLE_FILEPATH)
    nm = nmap.PortScanner()
    clients = get_clients(f"{GATEWAY_FANGED[0]}.{GATEWAY_FANGED[1]}.{GATEWAY_FANGED[2]}.{GATEWAY_FANGED[3]}/24", mac_table, nm)

    map_network(clients, nm)

    edges, vertices = get_graph_components(clients)
    draw_graph(edges, vertices)

    get_os_info(clients, nm)

    out = {client.ip : client.to_map() for client in clients.values()}

    with open("clients.json", "w") as outfile:
        json.dump(out, outfile)