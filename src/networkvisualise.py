# from ping3 import ping
import traceroute
import igraph as ig
import matplotlib.pyplot as plt
import socket

edges = []
verticies = []

icmp_socket, udp_socket = traceroute.init_sockets()

# Some random websites, hopefully from around the world
known_ips = ["google.com", "facebook.com", "maps.google.com", "packetswitch.co.uk"]

for current_ip in known_ips:
    if (traceroute.ping(current_ip, icmp_socket, udp_socket) != None):
        print(f"Found IP: {current_ip} in network, tracing path.")
        current_path = traceroute.trace(socket.gethostbyname(current_ip), icmp_socket, udp_socket)
        print("Path traced, constructing graph for current IP.")
        previous_hostname = None
        for node in current_path:

            # Set the vertex name to the hostname if possible
            current_hostname = node[1]
            if (current_hostname == "UNKNOWN"):
                current_hostname = node[0]

            # Don't add the same vertex twice!
            if (current_hostname not in verticies):
                verticies.append(current_hostname)
            
            if (previous_hostname != None):
                edges.append((verticies.index(previous_hostname), verticies.index(current_hostname)))
            previous_hostname = current_hostname
        print("Graph constructed, ready for next address")
    else:
        print(f"Could not reach {current_ip}, continuing")

print("Graph constructed, initialising visualisation")

n_vertices = len(verticies)


graph = ig.Graph(n_vertices, edges)

graph["title"] = "Network Visualisation"

# Vertex name is hostname if found, otherwise make it the IP of the node.
graph.vs["name"] = verticies

fig, ax = plt.subplots(figsize=(5,5))
ig.plot(
    graph,
    target=ax,
    vertex_size=0.1,
    vertex_frame_width=4.0,
    vertex_frame_color='white',
    vertex_label=graph.vs["name"],
    vertex_label_size=7.0,
    edge_color='black'
)

plt.show()

icmp_socket.close() 
udp_socket.close()