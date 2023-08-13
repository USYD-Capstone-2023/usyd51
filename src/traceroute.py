# Allows us to map the route from the host computer to any ip on a network.
# At the minute is setup for remote servers with known hostnames as its hard to test on a network as flat as mine...

import socket
import struct
import subprocess

# UDP port
PORT = 33434
MAX_HOPS = 30

def init_sockets():
    # Request timeout information
    timeout_data = struct.pack("ll", 1, 0)

    # Initialize sockets
    icmp_proto = socket.getprotobyname("icmp")
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_proto)
    icmp_socket.bind(("", PORT))
    icmp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout_data)

    udp_proto = socket.getprotobyname("udp")
    udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM, udp_proto)

    return icmp_socket, udp_socket


def trace(target_ip, icmp_socket, udp_socket):

    print(f"Tracing route from {socket.gethostname()} to {target_ip}")

    ttl = 1
    while ttl < MAX_HOPS:

        # Sends a message on UDP to the target with a limited ttl
        udp_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        udp_socket.sendto(b"", (target_ip, PORT))

        attempts = 2
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

                print(f"Hopped to {ip[0]} ({host_name}); ttl: {ttl}")
            
                # Ends if the target was reached
                if ip[0] == target_ip:
                    print(f"Reached target in {ttl} hops\n")
                    return  
                
                break          

        # Increments ttl to get the next router in the path
        ttl += 1
    
    print(f"Failed to reach target: {target_ip}\n")


# Pings the target_ip and returns whether it is up or not.
# Note that this is not portable, and will not work on windows. This will be changed later
def ping(target_ip, icmp_socket, udp_socket):

    try:
        subprocess.call("ping -c 1 %s > /dev/null" % (target_ip), shell=True, timeout=0.5)
        return True
    except subprocess.TimeoutExpired :
        return False;

# Returns a list of all active ips on the lan
def get_addresses(icmp_socket, udp_socket):

    print("Getting active devices on 192.168.1.xxx")
    ret = []
    # Small range just for testing convenience
    for i in range(1,40):
        ip = "192.168.1.%d" % (i)
        if ping(ip, icmp_socket, udp_socket):
            print("%s is up!" % (ip))
            ret.append(ip)

    return ret

def main():

    icmp_socket, udp_socket = init_sockets()

    # Traces the route from the host to all other active devices on the network
    ip_ls = get_addresses(icmp_socket, udp_socket)

    print("\nTracing routes...\n")
    for ip in ip_ls:
        trace(ip, icmp_socket, udp_socket)

    icmp_socket.close() 
    udp_socket.close()

if __name__ == "__main__":
    main()
