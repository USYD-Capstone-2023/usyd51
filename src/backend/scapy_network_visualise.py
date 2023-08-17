import scapy.all as scapy
import igraph as ig
import matplotlib.pyplot as plt
import json
from Client import Client
from MAC_table import MAC_table
import nmap
import socket as s


# This is a problem as you either have one gateway or the other. 
# Im 1.1 and yall are 0.1

# GATEWAY = "192.168.0.1"
GATEWAY = "192.168.1.1"
GATEWAY_FANGED = GATEWAY.split(".")
MAC_TABLE_FILEPATH = "../cache/oui.csv"


def get_nm_data(nm, ip, args):

    data = nm.scan(ip, arguments="-O -R --max-retries 0 --max-rtt-timeout 200ms")
    data = data["scan"]

    hostname = ip
    os_type = "unknown"
    os_vendor = "unknown"
    os_family = "unknown"

    if ip in data.keys():
        if "osmatch" in data[ip] and len(data[ip]["osmatch"]) > 0:
            osmatch = data[ip]["osmatch"][0]
            if 'osclass' in osmatch and len(osmatch["osclass"]) > 0:
                osclass = osmatch["osclass"][0]

                os_type = osclass["type"]
                os_vendor = osclass["vendor"]
                os_family = osclass["osfamily"]

        hostname = data[ip]["hostnames"][0]["name"]
        hostname = ip if hostname == "" else hostname

    return "device name: %s\ndevice type: %s\nOS vendor: %s\nOS family: %s" % (hostname, os_type, os_vendor, os_family)


def arp_scan(ip_range, clients, mac_table, nm):

    # Creating arp packet
    arp_frame = scapy.ARP(pdst=ip_range)
    ethernet_frame = scapy.Ether(dst="FF:FF:FF:FF:FF:FF")
    request = ethernet_frame / arp_frame

    # Run arp scan to retrieve active ips
    responded = scapy.srp(request, timeout=1, retry=2, verbose=False)[0]

    for response in responded:

        ip = response[1].psrc
        mac = response[1].hwsrc

        # resolves hostname if possible as well as the OS details by tcp fingerprinting
        name = get_nm_data(nm, ip, "-O -R --max-retries 0 --max-rtt-timeout 200ms")
        vendor = mac_table.find_vendor(mac)

        clients[ip] = Client(ip, name, mac, vendor)


def get_clients(ip_range, mac_table, nm):

    print("[INFO] Getting active devices on local network...")
    # Adding this computer to list of clients in the map
    own_ip = scapy.get_if_addr(scapy.conf.iface)
    own_mac = scapy.Ether().src
    # own_name = s.getfqdn(own_ip)
    own_name = "ja"
    own_vendor = mac_table.find_vendor(own_mac)

    own_name = s.gethostname()
    clients = {own_ip : Client(own_ip, own_name, own_mac, own_vendor)}

    gateway_name = get_nm_data(nm, GATEWAY, "-O -R --max-retries 0 --max-rtt-timeout 200ms")
    clients[GATEWAY] = Client(GATEWAY, gateway_name, "UNKNOWN", "UNKNOWN")

    arp_scan(ip_range, clients, mac_table, nm)

    print("[INFO] Found %d devices!" % (len(clients)))

    return clients


# Gets the ip of all devices on the path from the host to the target ip
def traceroute(ip, clients, nm):

    print("[INFO] Tracing route to %s" % (ip))

    # Runs traceroute.
    # Emits TCP packets with incrementing ttl until the target is reached
    # answers = scapy.srp(scapy.IP(dst=ip, ttl=(1, 30))/scapy.TCP(dport=53, flags="S"), timeout=3, verbose=False)[0]
    answers = scapy.traceroute(ip, verbose=False)[0]

    addrs = [GATEWAY]
    prev_resp_ip = GATEWAY

    for response_idx in range(1, len(answers)):

        if answers[response_idx].answer.src == prev_resp_ip:
            break

        resp_ip = answers[response_idx].answer.src

        if resp_ip not in clients.keys():

            clients[resp_ip] = Client(resp_ip, get_nm_data(nm, ip, "-O -R --max-retries 0 --max-rtt-timeout 200ms"), "UNKNOWN", "UNKNOWN")

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

    vertices = [clients[key].name for key in clients.keys()]

    gateway_client = clients[GATEWAY]
    layer = [gateway_client]
    visited = set()

    # Generates all edges
    read_layer = True
    while layer:

        if read_layer:
            for client in layer:
                for neighbour in client.neighbours:
                    v1 = min(vertices.index(client.name), vertices.index(neighbour.name))
                    v2 = max(vertices.index(client.name), vertices.index(neighbour.name))
                    edges.add((v1, v2))

        read_layer = not read_layer
        next_layer = []

        for client in layer:
            visited.add(client)
            for neighbour in client.neighbours:
                if neighbour not in visited:
                    next_layer.append(neighbour)

        layer = next_layer

    draw_graph(edges, vertices)

    out = {}
    for client in clients.keys():
        c = clients[client]
        out[client] = {"name" : c.name, "mac" : c.mac, "vendor" : c.vendor, "neighbours" : [x.name for x in c.neighbours]}

    with open("clients.json", "w") as outfile:
        json.dump(out, outfile)