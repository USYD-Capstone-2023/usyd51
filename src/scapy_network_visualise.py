import scapy.all as scapy
import igraph as ig
import matplotlib.pyplot as plt
import re, socket
import json
from mac_vendor_lookup import MacLookup


GATEWAY = "192.168.0.1"
GATEWAY_FANGED = GATEWAY.split(".")

def arp_scan(ip_range, clients):

    # Creating arp packet
    arp_frame = scapy.ARP(pdst=ip_range)
    ethernet_frame = scapy.Ether(dst="FF:FF:FF:FF:FF:FF")
    request = ethernet_frame / arp_frame

    # Run arp scan to retrieve active ips
    responded = scapy.srp(request, timeout=1, retry=10, verbose=False)[0]

    for response in responded:

        ip = response[1].psrc
        mac = response[1].hwsrc
        print(ip)

        # resolves hostname if possible. Massive time cost here, need to find a better solution +++
        name = ip
        # try:
        #     name = socket.gethostbyaddr(ip)[0]
        # except:
        #     pass
        vendor = "UNKNOWN"
        try:
            vendor = find_vendor(mac)
        except:
            pass
        clients[ip] = {"mac" : mac, "name" : name, "route" : [], "Vendor": vendor}


def tcp_scan(ip_range, clients):

    try:
        syn = scapy.IP(dst=ip_range) / scapy.TCP(dport=[80, 443], flags="S")
    except socket.gaierror:
        raise ValueError('Hostname {} could not be resolved.'.format(ip))

    responded = scapy.sr(syn, timeout=2, retry=8)[0]

    print("Discovered %d devices!\nResolving hostnames..." % (len(responded)))
    # Gather and store all relevant data for current client
    cursor = 0
    for response in responded:

        ip = response[1][scapy.IP].src
        mac = "na"

        # resolves hostname if possible. Massive time cost here, need to find a better solution +++
        name = ip
        # try:
        #     name = socket.gethostbyaddr(ip)[0]
        # except:
        #     pass

        clients[ip] = {"mac" : mac, "name" : name, "route" : []}

mac = MacLookup()
mac.update_vendors()  # <- This can take a few seconds for the download

def find_vendor(mac_address):
    return mac.lookup(mac_address)


def get_clients(ip_range):

    print("Getting active devices on local network...")

    # Adding this computer to list of clients in the map
    own_ip = scapy.get_if_addr(scapy.conf.iface)
    own_mac = scapy.Ether().src
    own_name = own_ip
    try:
        own_name = socket.gethostbyaddr(own_ip)[0]
    except:
        pass

    clients = {own_ip : {"mac" : own_mac, "name" : own_name, "route" : [own_ip, GATEWAY], "Vendor": find_vendor(own_mac)}}
    # tcp_scan("192.168.1.0/24", clients)
    # for i in range(5):
    arp_scan(f"{GATEWAY}/24", clients)

    return clients

# Gets the ip of all devices on the path from the host to the target ip
def tcp_traceroute(ip):

    print("Tracing route to %s" % (ip))

    # Runs traceroute.
    # Emits TCP packets with incrementing ttl until the target is reached
    answers = scapy.srp(scapy.IP(dst=ip, ttl=(1, 30))/scapy.TCP(dport=53, flags="S"), timeout=3, verbose=False)[0]
    # answers = scapy.traceroute(ip, verbose=False)[0]

    addrs = [GATEWAY]
    for response in answers:

        resp_ip = response.answer.src
        if resp_ip != addrs[len(addrs) - 1]:
            addrs.append(resp_ip)

    if ip not in addrs:
        addrs.append(ip)

    return addrs

# Prints network visualisation
def draw_graph(edges, vertices):

    print("Graph constructed, initialising visualisation")

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

    clients = get_clients(f"{GATEWAY_FANGED[0]}.{GATEWAY_FANGED[1]}.{GATEWAY_FANGED[2]}/24.{GATEWAY_FANGED[3]}/24")

    with open("clients.json", "w") as outfile:
        json.dump(clients, outfile)

    route_clients = {}
    vertices = []
    edges = set()
    for client in clients.keys():

        data = clients.get(client)
        route = tcp_traceroute(client)
        data["route"].extend(route)

        # Creates a dictionary of all clients including those found in the path
        route_clients[client] = data
        # Generates all vertices
        for ip in data["route"]:
            if ip in route_clients.keys():
                continue

            elif ip in clients.keys():
                route_clients[ip] = clients.get(ip)
                route_clients[ip]["route"].extend(route)
                vertices.append(clients[ip]["name"])

            else:
                route_clients[ip] = {"mac" : "UNKNOWN", "name" : ip, "route" : route}
                vertices.append(ip)
            
    # Generates all edges
    for client in route_clients:
        prev_client_name = None
        for ip in route_clients.get(client)["route"]:

            client_name = ip
            if ip in route_clients.keys():
                client_name = route_clients[ip]["name"]

            if prev_client_name and prev_client_name != client_name:
                if client_name not in vertices:
                    vertices.append(client_name)

                if prev_client_name not in vertices:
                    vertices.append(prev_client_name)

                i1 = vertices.index(prev_client_name)
                i2 = vertices.index(client_name)

                edges.add((min(i1, i2), max(i1, i2)))

            prev_client_name = client_name

    draw_graph(edges, vertices)