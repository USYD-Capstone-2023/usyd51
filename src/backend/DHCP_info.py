from scapy.all import *
import time, threading

TIMEOUT = 10

def get_dhcp_server_info():

    dhcp_server_info = {}
    event = threading.Event()
    start = time.time()

    # Callback function waits for a DHCP response packet to arrive and quits 
    # if it finds a valid one. Runs in its own thread
    def dhcp_response(pkt):
        
        for option in pkt[DHCP].options:
            if option == "end" or  option == "pad" or (option[0] == "message-type" and option[1] == 1):
                break

            
            if type(option[1]) == bytes:
                dhcp_server_info[str(option[0])] = option[1].decode("utf-8")
                continue

            dhcp_server_info[str(option[0])] = str(option[1])


    def stop_filter(_):
        return time.time() - start > TIMEOUT or len(dhcp_server_info.keys()) > 0


    def start_sniff_thread(iface):
        sniff(prn=dhcp_response, filter="udp and (port 67 or 68)", store=1, stop_filter=stop_filter)
        event.set()


    # Getting mac address
    mac = get_if_raw_hwaddr(conf.iface)[1]

    # Creating DHCP discovery packet
    eth = Ether(dst='ff:ff:ff:ff:ff:ff', src=mac, type=0x0800)
    ip = IP(src='0.0.0.0', dst='255.255.255.255')
    udp = UDP(dport=67,sport=68)
    bootp = BOOTP(op=1, chaddr=mac)
    dhcp = DHCP(options=[('message-type','discover'), ('end')])
    request = eth / ip / udp / bootp / dhcp

    # Starts a listener thread that waits until it receives a response
    sniffer = threading.Thread(target=start_sniff_thread, args=(conf.iface,))
    sniffer.start()

    # Sends DHCP request packet until it times out or receives a valid response
    while not event.is_set():
        sendp(request, iface=conf.iface, verbose=False)

    sniffer.join()
    # Gives error if no response arrives
    if len(dhcp_server_info.keys()) == 0:
        dhcp_server_info = {"error" : "Recieved no response from dhcp server after %d seconds..." % (TIMEOUT)}
        print("[ERR ] Recieved no response from DHCP server after %d seconds..." % (TIMEOUT))

    return dhcp_server_info