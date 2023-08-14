import old_traceroute as traceroute
import igraph as ig
import matplotlib.pyplot as plt


destination = input("Enter the ip address or url of the destination: ")
if (destination == ""):
    destination = "google.com"
    print("No IP entered, defaulting to google.com")
locations = traceroute.get_ip_route(destination)
n_vertices = len(locations)
edges = [(i, i+1) for i in range(len(locations)-1)]


graph = ig.Graph(n_vertices, edges)

graph["title"] = "Network Visualisation"

# Vertex name is hostname if found, otherwise make it the IP of the node.
graph.vs["name"] = [x[1] if x[1] != "UNKNOWN" else x[0] for x in locations]

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



