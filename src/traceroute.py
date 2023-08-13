# Allows us to map the route from the host computer to any ip on a network.
# At the minute is setup for remote servers with known hostnames as its hard to test on a network as flat as mine...

import socket
import struct

# UDP port
port = 33434
max_hops = 30

def get_ip_route(dest_ip):
    # Initialize sockets
    icmp_proto = socket.getprotobyname("icmp")
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_proto)

    udp_proto = socket.getprotobyname("udp")
    udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM, udp_proto)

    # Request timeout information
    timeout_data = struct.pack("ll", 1, 0)

    icmp_socket.bind(("", port))
    icmp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout_data)

    # Temporary target for basic implementation, final version will do a ping sweep to get all connected local addresses, then trace
    # the route to those. 
    target = dest_ip
    target_ip = socket.gethostbyname(target)

    # print(f"Tracing route from {socket.gethostname()} to {target_ip} ({target})")

    ttl = 1
    found_target = False



    # Generate a list of ip-addresses and hostnames while traversing
    found = []

    while ttl < max_hops and not found_target:

        # Sends a message on UDP to the target with a limited ttl
        udp_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        udp_socket.sendto(b"", (target_ip, port))

        attempts = 5
        responded = False

        # Awaits an ICMP response from a router on the path stating that ttl has expired, or the goal has been reached
        while attempts > 0:

            # Gets information of the router that responded and prints it
            try:
                responded = True
                pack, ip = icmp_socket.recvfrom(512)
            except socket.error:
                attempts -= 1
                continue
        
            if responded:
                host_name = "UNKNOWN"
                try:
                    # Resolves hostname if possible. 
                    # As far as i can tell this will be a bit more difficult on LAN
                    host_name = socket.gethostbyaddr(ip[0])[0]
                except:
                    pass

                # print(f"Hopped to {ip[0]} ({host_name}); ttl: {ttl}")
                found.append((ip[0], host_name));
            
                # Ends if the target was reached
                if ip[0] == target_ip:
                    found_target = True
            
                break 

        # Increments ttl to get the next router in the path
        ttl += 1

    # print(f"Reached target in {ttl} hops")
    return found




