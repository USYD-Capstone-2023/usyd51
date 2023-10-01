import ssl
import socket
import OpenSSL
from scapy.all import *



def get_ssl_certificate_details(ip, port=443):
    try:
        # Create a socket and connect to the IP and port
        sock = socket.create_connection((ip, port))

        # Create an SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ssl_sock = context.wrap_socket(sock, server_hostname=ip)

        # Get the SSL certificate
        certificate = ssl_sock.getpeercert()

        # Print certificate details
        print("Certificate Details:")
        print(f"Subject: {certificate['subject']}")
        print(f"Issuer: {certificate['issuer']}")
        print(f"Valid From: {certificate['notBefore']}")
        print(f"Valid Until: {certificate['notAfter']}")
        
        # Extract and print alternative subject names (e.g., DNS names)
        alt_names = certificate.get('subjectAltName', [])
        if alt_names:
            print("Alternative Subject Names:")
            for name_type, name in alt_names:
                print(f"{name_type}: {name}")

        # Optionally, you can print the entire certificate as well
        # print(crypto.dump_certificate(crypto.FILETYPE_TEXT, certificate))

        # Close the socket
        ssl_sock.close()
    except socket.error as e:
        print(f"Error: {e}")
    except ssl.SSLError as e:
        print(f"SSL Error: {e}")

def check_port(ip, port):


    
    try:
        # Create a TCP SYN packet to check if the port is open
        response = sr1(IP(dst=ip) / TCP(dport=port, flags="S"), timeout=1, verbose=False)

        if response and response.haslayer(TCP):
            if response.getlayer(TCP).flags == 0x12:  # TCP SYN-ACK flag
                return True #return True if the port is open
            else:
                return False #return false if the port is closed
        else:
            return False #return false if the port is closed
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def in_class_A(ip):
    A_ip_range = [[10, 0, 0, 0], [10, 255, 255, 255]]
    ip = ip.split(".")
    ip = [int(x) for x in ip] 
    if ip[0] == 10:
        return True
    else:
        return False
    
def in_class_B(ip):
    B_ip_range = [[172,16,0,0], [172, 31, 255, 255]]
    ip = ip.split(".")
    ip = [int(x) for x in ip] 
    if ip[0] == 172:
        if ip[1] >= 16 and ip[1] <= 31:
            return True
    return False

def in_class_C(ip):
    C_ip_range = [[192, 168, 0, 0], [192, 168, 255, 255]]
    ip = ip.split(".")
    ip = [int(x) for x in ip] 
    #print(ip)
    if ip[0] == 192:
        #print(196)
        if ip[1] == 168:
            #print(168)
            return True
    return False

def vertical_traceroute(target_host="8.8.8.8"):
    # Define the target host (in this case, Google's DNS server)
    # Create a list to store the traceroute results
    traceroute_results = []

    # Perform the traceroute
    for ttl in range(1, 31):  # Set the maximum TTL to 30
        # Create an ICMP echo request packet with the specified TTL
        packet = IP(dst=target_host, ttl=ttl) / ICMP()

        # Send the packet and receive a reply
        reply = sr1(packet, verbose=False, timeout=1)

        if reply is not None:
            traceroute_results.append(reply.src)

        # Check if we have reached the target host
        if reply and reply.src == target_host:
            break

    local_vertical = []
    # Print the traceroute results
    for i, ip in enumerate(traceroute_results):
        if in_class_A(ip) or in_class_B(ip) or in_class_C(ip):
            local_vertical.append(ip)
    
    return local_vertical

if __name__ == "__main__":
    ips = ["1","60","82","102","141","145","162","171","172","173","177","179","191","205","210","219","225","245","249"]  # Replace with your target host
    target_port = 443  # Replace with the appropriate SSL port

    print(vertical_traceroute("8.8.8.8"))

    #get_ssl_certificate_details("192.168.0.1")

    #for ip in ips:
    #    ip = "192.168.0." + ip
    #    if check_port(ip, target_port):
    #        print(ip)

    #check_ssl_certificate(target_host, target_port)


