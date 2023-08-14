import scapy.all as scapy
import igraph as ig
import matplotlib.pyplot as plt
import re, socket

MAX_HOPS = 10
GATEWAY = "192.168.1.1"

def get_ip_mac(ip_range):

    # Creating arp packet
    arp_frame = scapy.ARP(pdst=ip_range)
    ethernet_frame = scapy.Ether(dst="FF:FF:FF:FF:FF:FF")
    request = ethernet_frame / arp_frame

    clients = {}

    # Runs ARP scan on all available network interfaces
    for iface in scapy.IFACES.data.keys():

        if iface == "lo":
            continue

        # Emit request packet
        responded = scapy.srp(request, timeout=2, retry=3, iface=iface, verbose=False)[0]

        print("Discovered %d devices!\nResolving hostnames..." % (len(responded)))
        # Gather and store all relevant data for current client
        for response in responded:

            ip = response[1].psrc
            mac = response[1].hwsrc

            # resolves hostname if possible
            name = ip
            try:
                name = socket.gethostbyaddr(ip)[0]
            except:
                pass

            clients[ip] = {"mac" : mac, "name" : name, "route" : []}

    print(clients)

    return clients

# Gets the ip of all devices on the path from the host to the target ip
def tcp_traceroute(ip, gateway):

    print("Tracing route to %s" % (ip))

    # Runs traceroute.
    # Emits TCP packets with incrementing ttl until the target is reached
    answers = scapy.sr(scapy.IP(dst=ip, ttl=(1, MAX_HOPS))/scapy.TCP(dport=53, flags="S"), timeout=3, verbose=False)[0]

    addrs = [gateway]
    for response in answers:

        ip = response.answer.src
        if not addrs or ip != addrs[len(addrs) - 1]:
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

    fig, ax = plt.subplots(figsize=(5,5))
    ig.plot(
        graph,
        target=ax,
        vertex_size=0.1,
        vertex_frame_width=4.0,
        vertex_frame_color='white',
        vertex_label=graph.vs["name"],
        vertex_label_size=7.0,
        vertex_label_dist=3.0,
        edge_color='black'

    )

    plt.show()

if __name__ == "__main__":
    clients = get_ip_mac("192.168.1.0/24")

    vertices = []
    edges = set()
    for client in clients.keys():

        data = clients.get(client)
        route = tcp_traceroute(client, GATEWAY)
        data["route"].extend(route)

        prev_client_name = None
        for ip in route:

            client_name = clients[ip]["name"]
            if client_name not in vertices:
                vertices.append(client_name)

            if prev_client_name:

                edges.add((vertices.index(prev_client_name), vertices.index(client_name)))

            prev_client_name = client_name

    draw_graph(edges, vertices)