# External
from scapy.all import (
    traceroute,
    conf,
    ARP,
    DNSRR,
    UDP,
    IP,
    Ether,
    srp1,
    get_if_addr,
    sniff,
    RandShort,
)

# Local
from threadpool import Threadpool
from job import Job
from MAC_table import MAC_table
from device import Device
from platform import system
import nmap, socket, netifaces, threading, sys, signal, pywifi, time

MAC_TABLE_FP = "../cache/oui.csv"
NUM_THREADS = 25

class Net_tools:
    def __init__(self, db, lb):

        if NUM_THREADS < 1:
            print("[ERR ] Thread count cannot be less than 1. Exitting...")
            sys.exit(-1)

        self.db = db
        self.lb = lb
        self.threadpool = Threadpool(NUM_THREADS)

        # Set signal handler to gracefully terminate threadpool on shutdown
        signal.signal(signal.SIGTERM, self.cleanup)
        signal.signal(signal.SIGINT, self.cleanup)

        self.mac_table = MAC_table(MAC_TABLE_FP)

        # Retrieves dhcp server information (router ip, subnet mask, domain name)
        self.dhcp_server_info = Net_tools.get_dhcp_server_info()

        self.gateway = self.dhcp_server_info["router"]
        self.subnet_mask = self.dhcp_server_info["subnet_mask"]
        self.domain = self.dhcp_server_info["domain"]
        self.iface = self.dhcp_server_info["iface"]
        self.gateway_mac = Net_tools.arp_helper(self.gateway)[1]
        self.name = None


    # Signal handler to gracefully end the threadpool on shutdown
    def cleanup(
        self,
        *args,
    ):
        self.threadpool.end()
        print("Finished cleaning up! Server will now shut down.")
        sys.exit()


    # --------------------------------------------- ON START -------------------------------------- #

    def new_network(self, name):

        self.name = name
            # Creates a new table in the database for the current network if it doesnt already exist
        self.db.register_network(self.gateway_mac, self.domain, self.name)

        self.client_mac = Ether().src

        # Creates a device object for the client device if one doesnt already exist
        if not self.db.contains_mac(self.gateway_mac, self.client_mac):
            client_device = Device(get_if_addr(conf.iface), self.client_mac)
            client_device.hostname = socket.gethostname()
            client_device.mac_vendor = self.mac_table.find_vendor(client_device.mac)
            self.db.add_device(self.gateway_mac, client_device)

        # Creates device object to represent the gateway if one doesnt exist already
        if not self.db.contains_mac(self.gateway_mac, self.gateway_mac):
            gateway_device = Device(self.gateway, self.gateway_mac)
            gateway_device.hostname = self.domain
            self.db.add_device(self.gateway_mac, gateway_device)

        DNS_sniffer = threading.Thread(target=self.run_wlan_sniffer, args=(conf.iface,))
        DNS_sniffer.daemon = True
        DNS_sniffer.start()


    # --------------------------------------------- SSID ------------------------------------------ #

    def get_ssid(self):

        current_system = system()
        # MacOS - Get by running the airport program.
        if current_system == "Darwin":
            import subprocess

            process = subprocess.Popen(
                [
                    "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport",
                    "-I",
                ],
                stdout=subprocess.PIPE,
            )
            out, err = process.communicate()
            process.wait()
            for line in out.decode("utf8").split("\n"):
                if " SSID" in line:
                    return line.split(": ")[1]
        

        wifi = pywifi.PyWiFi()
        ifaces = wifi.interfaces()

        if len(ifaces) < 1:
            return "Disconnected"

        iface = ifaces[0]
        # Exponential dropoff
        results = []
        for exp in range(6):
            # Start scan and wait for results
            iface.scan()
            time.sleep(0.1 * pow(2, exp))
            results = iface.scan_results()

            if len(results) > 0:
                break

        if results:
            # TODO fix
            print(f"Seems to return the strongest signal, not the current connected one... {[x.ssid for x in results]}")
            return results[0].ssid

        return "Disconnected"


    # ---------------------------------------------- MAC VENDOR ---------------------------------------------- #

    # Updates the mac vendor field of all devices in the current network's table of the database
    def add_mac_vendors(self):

        # Retrieves all devices from database
        devices = self.db.get_all_devices(self.gateway_mac)

        # Set loading bar
        self.lb.set_params("Resolving MAC Vendors", 40, len(devices.keys()))
        self.lb.show()

        # Adds mac vendor to device and saves to database
        for device in devices.values():
            device.mac_vendor = self.mac_table.find_vendor(device.mac)
            self.db.save_device(self.gateway_mac, device)
            self.lb.increment()
            self.lb.show()

        self.lb.reset()

    # ---------------------------------------------- ARP SCANNING ---------------------------------------------- #

    # Sends an ARP ping to the given ip address to check it is alive and retrieve its MAC
    def arp_helper(ip):

        # Creating ARP packet
        arp_frame = ARP(pdst=ip)
        ethernet_frame = Ether(dst="FF:FF:FF:FF:FF:FF")
        request = ethernet_frame / arp_frame

        # Send/recieve packet
        response = srp1(request, timeout=0.5, retry=2, verbose=False)

        # Formulate return values
        found_ip = None
        found_mac = None

        if response:
            found_ip = response[0][1].psrc
            found_mac = response[0][1].hwsrc

        return found_ip, found_mac


    # Gets all active active devices on the network
    def get_devices(self):

        print("[INFO] Getting all active devices on network.")

        # Breaks subnet and gateway ip into bytes
        sm_split = self.subnet_mask.split(".")
        gateway_split = self.gateway.split(".")
        first_ip = [0] * 4
        last_ip = [0] * 4

        # Calculates first and last IPs byte by byte, based off subnet mask and router IP
        for i in range(4):
            sm_chunk = int(sm_split[i])
            gateway_chunk = int(gateway_split[i])

            first_ip[i] = sm_chunk & gateway_chunk
            sm_inv = (1 << 8) - 1 - sm_chunk
            last_ip[i] = sm_inv | (sm_chunk & gateway_chunk)

        # Generates return array of size equal to the number of IPs in the range
        num_addrs = 1
        for i in range(4):
            num_addrs *= max(last_ip[i] - first_ip[i] + 1, 1)

        returns = [-1] * num_addrs

        # Set loading bar
        self.lb.set_params("Scanning for active devices", 40, num_addrs)
        self.lb.show()

        # Preparing thread job parameters
        mutex = threading.Lock()
        cond = threading.Condition(lock=mutex)
        counter_ptr = [0]

        # The current job, for referencing the return location for the thread
        job_counter = 0

        # Iterates over full IP range
        for p1 in range(first_ip[0], last_ip[0] + 1):
            for p2 in range(first_ip[1], last_ip[1] + 1):
                for p3 in range(first_ip[2], last_ip[2] + 1):
                    for p4 in range(first_ip[3], last_ip[3] + 1):
                        # Creates job and adds to threadpool queue for execution
                        ip = "%d.%d.%d.%d" % (p1, p2, p3, p4)
                        job = Job(
                            fptr=Net_tools.arp_helper,
                            args=ip,
                            ret_ls=returns,
                            ret_id=job_counter,
                            counter_ptr=counter_ptr,
                            cond=cond,
                        )
                        job_counter += 1

                        if not self.threadpool.add_job(job):
                            return "Request size over maximum allowed size %d" % (
                                self.threadpool.MAX_QUEUE_SIZE
                            )

        # Waits for all tasks to be completed by the threadpool
        mutex.acquire()
        while counter_ptr[0] < num_addrs:
            cond.wait()
            self.lb.set_progress(counter_ptr[0])
            self.lb.show()

        mutex.release()

        # Creates a device object for each ip and mac, saves to database
        for i in range(num_addrs):
            ip = returns[i][0]
            mac = returns[i][1]
            if mac and ip and not self.db.contains_mac(self.gateway_mac, mac):
                self.db.add_device(self.gateway_mac, Device(ip, mac))

        print(
            "\n[INFO] Found %d devices!\n"
            % (len(self.db.get_all_devices(self.gateway_mac)))
        )
        self.lb.reset()

    # ---------------------------------------------- TRACEROUTE ---------------------------------------------- #

    # Thread worker to get path to provided ip address
    def traceroute_helper(args):

        ip = args[0]
        gateway = args[1]

        # Remove loops on gateway
        if ip == gateway:
            return []

        # This one seems to have issues, but doesnt give mac res errors

        # Emits UDP packets with incrementing ttl until the target is reached
        # answers = traceroute(ip, l4=UDP(sport=RandShort()), maxttl=10, iface=conf.iface, verbose=False)[0]
        answers = traceroute(ip, maxttl=10, iface=conf.iface, verbose=False)[0]
        addrs = [gateway]

        for response_idx in range(1, len(answers)):
            # Dont register if the packet hit the same router again
            if answers.res[0][1].src == addrs[-1] or answers.res[0][1].src == ip:
                break

            addrs.append(answers.res[0][1].src)

        return addrs

    # Runs a traceroute on all devices in the database to get their neighbours in the routing path, updates and saves to database
    def add_routes(self):

        print("[INFO] Tracing Routes...")

        # Retrieve network devices from database
        devices = self.db.get_all_devices(self.gateway_mac)
        device_addrs = set()

        # Set loading bar
        self.lb.set_params("Tracing routes to devices", 40, len(devices.keys()))
        self.lb.show()

        # Preparing thread job parameters
        mutex = threading.Lock()
        cond = threading.Condition(lock=mutex)
        counter_ptr = [0]
        returns = [-1] * len(devices.keys())

        # The current job, for referencing the return location for the thread
        job_counter = 0

        for device in devices.values():
            # Creates job and adds to threadpool queue for execution
            device_addrs.add(device.ip)
            job = Job(
                fptr=Net_tools.traceroute_helper,
                args=(device.ip, self.gateway),
                ret_ls=returns,
                ret_id=job_counter,
                counter_ptr=counter_ptr,
                cond=cond,
            )
            job_counter += 1

            if not self.threadpool.add_job(job):
                return "Request size over maximum allowed size %d" % (
                    self.threadpool.MAX_QUEUE_SIZE
                )

        # Waits for all jobs to be completed by the threadpool
        mutex.acquire()
        while counter_ptr[0] < len(devices.keys()):
            cond.wait()
            self.lb.set_progress(counter_ptr[0])
            self.lb.show()

        mutex.release()
        print("[INFO] Traceroute complete!\n")

        # Parses output
        job_counter = 0
        for device in devices.values():
            parent = ""
            for addr in returns[job_counter]:
                # Adds devices to database if they don't already exist
                if addr not in device_addrs:
                    device_addrs.add(addr)
                    new_device = Device(addr, Net_tools.arp_helper(addr)[1])
                    new_device.parent = parent
                    self.db.add_device(self.gateway_mac, new_device)
                    devices = self.db.get_all_devices(self.gateway_mac)

                parent = addr

            # Updates the devices parent node
            if len(returns[job_counter]) > 0:
                device.parent = returns[job_counter][-1]
            else:
                device.parent = "unknown"

            self.db.save_device(self.gateway_mac, device)
            job_counter += 1

        self.lb.reset()

    # ---------------------------------------------- OS FINGERPRINTING ---------------------------------------------- #

    # Thread worker to get os info from the provided ip address
    def os_helper(ip):

        nm = nmap.PortScanner()
        # Performs scan
        data = nm.scan(ip, arguments="-O")
        data = data["scan"]

        os_info = {"os_type": "unknown", "os_vendor": "unknown", "os_family": "unknown"}

        # Parses output for os info
        if ip in data.keys():
            if "osmatch" in data[ip] and len(data[ip]["osmatch"]) > 0:
                osmatch = data[ip]["osmatch"][0]
                if "osclass" in osmatch and len(osmatch["osclass"]) > 0:
                    osclass = osmatch["osclass"][0]

                    os_info["os_type"] = osclass["type"]
                    os_info["os_vendor"] = osclass["vendor"]
                    os_info["os_family"] = osclass["osfamily"]

        return os_info

    def add_os_info(self):

        print("[INFO] Getting OS info...")

        if not self.db.contains_network(self.gateway_mac):
            return {
                "error": "Current network is not registered in the database, run /map_network to add this network to the database."
            }

        # Retrieve network devices from database
        devices = self.db.get_all_devices(self.gateway_mac)

        # Set loading bar
        self.lb.set_params("Scanned", 40, len(devices.keys()))
        self.lb.show()

        # Preparing thread job parameters
        mutex = threading.Lock()
        cond = threading.Condition(lock=mutex)
        counter_ptr = [0]
        returns = [-1] * len(devices.keys())

        # The current job, for referencing the return location for the thread
        job_counter = 0
        for device in devices.values():
            # Create job and add to threadpool queue for execution
            job = Job(
                fptr=Net_tools.os_helper,
                args=device.ip,
                ret_ls=returns,
                ret_id=job_counter,
                counter_ptr=counter_ptr,
                cond=cond,
            )
            job_counter += 1

            if not self.threadpool.add_job(job):
                return "Request size over maximum allowed size %d" % (
                    self.threadpool.MAX_QUEUE_SIZE
                )

        # Waits for all jobs to be completed
        mutex.acquire()
        while counter_ptr[0] < len(devices.keys()):
            cond.wait()
            self.lb.set_progress(counter_ptr[0])
            self.lb.show()

        mutex.release()

        # Sets all devices OS information
        job_id = 0
        for device in devices.values():
            device.os_type = returns[job_id]["os_type"]
            device.os_family = returns[job_id]["os_family"]
            device.os_vendor = returns[job_id]["os_vendor"]
            job_id += 1

        print("\n[INFO] OS scan complete!\n")

        # Reset loading bar for next task. Enables frontend to know job is complete.
        self.lb.reset()

    # ---------------------------------------------- HOSTNAME LOOKUP ---------------------------------------------- #

    # Thread worker for reverse DNS lookup
    def hostname_helper(addr):

        try:
            return socket.gethostbyaddr(addr)[0]
        except:
            return "unknown"

    # Retrieves the hostnames of all devices on the network and saves them to the database
    def add_hostnames(self):

        # Retrieve network devices from database
        devices = self.db.get_all_devices(self.gateway_mac)

        # Set loading bar
        self.lb.set_params("Resolving Hostnames", 40, len(devices.keys()))
        self.lb.show()

        # Preparing thread job parameters
        mutex = threading.Lock()
        cond = threading.Condition(lock=mutex)
        counter_ptr = [0]
        returns = [-1] * len(devices.keys())

        # Counts the number of dispatched jobs
        dispatched = len(devices.keys())

        # The current job, for referencing the return location for the thread
        job_counter = 0

        for device in devices.values():
            # If hostname has been found in wlan DNSRR sniffer, use it instead
            if device.hostname != "unknown":
                self.lb.increment()
                dispatched -= 1
                returns[job_counter] = device.hostname
                job_counter += 1
                continue

            # Create job and add to threadpool queue for execution
            job = Job(
                fptr=Net_tools.hostname_helper,
                args=device.ip,
                ret_ls=returns,
                ret_id=job_counter,
                counter_ptr=counter_ptr,
                cond=cond,
            )
            job_counter += 1

            if not self.threadpool.add_job(job):
                return "Request size over maximum allowed size %d" % (
                    self.threadpool.MAX_QUEUE_SIZE
                )

        # Wait for all jobs to be comleted
        mutex.acquire()
        while counter_ptr[0] < dispatched:
            cond.wait()
            self.lb.set_progress(counter_ptr[0] + (len(devices.keys()) - dispatched))
            self.lb.show()

        mutex.release()

        # Add returned hostnames to devices, save to database
        job_counter = 0
        for device in devices.values():
            if device.hostname != "unkown":
                device.hostname = returns[job_counter]
                self.db.save_device(self.gateway_mac, device)
            job_counter += 1

        print("[INFO] Name resolution complete!\n")

        # Reset loading bar for next task. Enables frontend to know job is complete.
        self.lb.reset()

    # ---------------------------------------------- DHCP INFO ---------------------------------------------- #

    # Gets the gateway, interface, subnet mask and domain name of the current network
    def get_dhcp_server_info():

        print("[INFO] Retrieveing DHCP server info...")

        gws = netifaces.gateways()

        # Failsafe defaults in the event that there is no network connection
        default_gateway = None
        default_iface = "unknown"
        subnet_mask = "255.255.255.0"
        domain = "unknown"

        print(gws)

        if "default" in gws.keys() and netifaces.AF_INET in gws["default"].keys():
            default_gateway = netifaces.gateways()["default"][netifaces.AF_INET][0]
            default_iface = netifaces.gateways()["default"][netifaces.AF_INET][1]
            subnet_mask = netifaces.ifaddresses(default_iface)[netifaces.AF_INET][0][
                "netmask"
            ]
            domain = Net_tools.hostname_helper(default_gateway)

        return {
            "router": default_gateway,
            "iface": default_iface,
            "subnet_mask": subnet_mask,
            "domain": domain,
        }

    # ---------------------------------------------- DNS SNIFFER ---------------------------------------------- #

    # Packet sniffing daemon to get hostnames
    def wlan_sniffer_callback(self, pkt):

        # Sniffs mDNS responses for new hostnames and devices
        if IP in pkt and UDP in pkt and pkt[UDP].dport == 5353:
            # Can only be saved to database if the network is registered
            if not self.db.contains_network(self.gateway_mac):
                return

            ip = pkt[IP].src
            mac = Net_tools.arp_helper(ip)[1]

            if mac == None:
                return

            # Add device to database if it doesnt exist
            if not self.db.contains_mac(self.gateway_mac, mac):
                device = Device(ip, mac)
                device.mac_vendor = self.mac_table.find_vendor(mac)
                device.parent = Net_tools.traceroute_helper((ip, self.gateway))[-2]
                self.db.add_device(self.gateway_mac, device)

            if DNSRR in pkt:
                # Exclude non-human names and addresses
                name = pkt[DNSRR].rrname.decode("utf-8")
                if name.split(".")[-2] != "arpa" and name[0] != "_":
                    # Update existing device and save to database if it already exists
                    device = self.db.get_device(self.gateway_mac, mac)
                    if device == None:
                        print("[DEBUG] err in wlan sniff")
                        return

                    device.hostname = name
                    self.db.save_device(self.gateway_mac, device)

    def run_wlan_sniffer(self, iface):
        sniff(prn=self.wlan_sniffer_callback, iface=iface)



    # Active DNS, LLMNR, MDNS requests, cant get these to work at the minute but theyll be useful
    # ---------------------------------------- WIP -----------------------------------------

    # iface = conf.iface

    # host_rev = "".join(["%s." % x for x in host.split(".")[::-1]]) + "in-addr.arpa"

    # query = Ether(src=own_mac, dst="FF:FF:FF:FF:FF:FF") / \
    #         IP(src=own_ip, dst="224.0.0.252") / \
    #         UDP(sport=60403, dport=5355)/ \
    #         LLMNRQuery(id=1, qd=DNSQR(qname=host_rev, qtype="PTR", qclass="IN"))

    # response = srp1(query)

    # if response and LLMNRResponse in response:
    #     name = response[LLMNRResponse].qd.qname.decode()
    #     print("resolved hostname: %s" % (name))
    #     print("ip: %d" % (response[LLMNRResponse].an.rdata))
    #     ret[host] = name

    # print(ret[host])

    # mdns_ip = "224.0.0.251"
    # mdns_mac = "01:00:5e:00:00:fb"

    # mdns_query = Ether(src=own_mac, dst=mdns_mac) / \
    #              IP(src=own_ip, dst=mdns_ip) / \
    #              UDP(sport=5353, dport=5353) / \
    #              DNS(rd=1, qd=DNSQR(qname=host_rev, qtype="PTR"))

    # responses, _ = srp(mdns_query, verbose=0, timeout=2)

    # for response in responses:
    #     if DNSRR in response[1] and response[1][DNSRR].type == 12:
    #         name = response[1][DNSRR].rdata.decode()
    #         print("resolved hostname: %s" % (name))
    #         ret[host] = name

    # print(ret[host])
    # try:
    #     ret[host] = socket.gethostbyaddr(host)
    # except:
    #     ret[host] = "unknown"
    # ---------------------------------------- WIP -----------------------------------------
