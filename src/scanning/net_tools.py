# External
from scapy.all import (
    traceroute,
    conf,
    ARP,
    IP,
    TCP,
    Ether,
    srp1,
    sr1,
    get_if_addr,
)

import nmap3, netifaces, requests

# Local
from job import Job
from mac_table import MACTable
from device import Device
from network import Network
from threadpool import Threadpool

# Stdlib
from platform import system
import socket, threading, subprocess, os
from datetime import datetime

MAC_TABLE_FP = "./oui/oui.csv"

class NetTools:

    _instance = None

    def __new__(cls, NUM_THREADS):
        if cls._instance == None:
            cls.instance = super(NetTools, cls).__new__(cls)
            cls.instance.threadpool = Threadpool(NUM_THREADS)
            cls.instance.mac_table = MACTable(MAC_TABLE_FP)
        return cls.instance
    

    def init_scan(self, network_id, iface=conf.iface):

        ts = int(datetime.now().timestamp())

        # Retrieves dhcp server information (router ip, subnet mask, domain name)
        dhcp_server_info = self.get_dhcp_server_info()
        gateway = dhcp_server_info["router"]
        domain = dhcp_server_info["domain"]

        # Wireguard tunnel
        # show_interfaces()
        # iface = dev_from_index(63) # you need to get this index for ur interface list

        gateway_mac = self.arp_helper(gateway, iface)[1]
        ssid = self.get_ssid(iface)

        # Creates a network with default name = ssid
        network = Network(ssid, ssid, ts, dhcp_server_info, gateway_mac, network_id)

        # Adds client device to network as they are implicitly connected
        client_device = Device(get_if_addr(iface), Ether().src)
        client_device.hostname = socket.gethostname()
        client_device.parent = gateway
        network.add_device(client_device)

        # Creates device object to represent the gateway if one doesnt exist already
        gateway_device = Device(gateway, gateway_mac)
        gateway_device.hostname = domain
        network.add_device(gateway_device)

        return network



    # --------------------------------------------- SSID ------------------------------------------ #

    def get_ssid(self, iface=conf.iface):

        current_system = system()

        # MacOS - Get by running the airport program.
        if current_system == "Darwin":

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

        elif current_system == "Linux":

            return os.popen("iwconfig " + iface + " | grep ESSID | awk '{print $4}' | sed 's/" + '"' + "//g' | sed 's/.*ESSID://'").read()[:-1]

        elif current_system == "Windows":
            ssid = subprocess.check_output("powershell.exe (get-netconnectionProfile)", shell=True). decode("utf-8")

            for entry in ssid.split("\r\n\r\n"):
                if "IPv4Connectivity         : Internet" in entry:
                    ssid = entry.split(":")[1].split("\r")[0].strip()
                    break
            
            if len(ssid) == 0:
                return "new network"
            
            return ssid

        return "OS UNSUPPORTED"

    # ---------------------------------------------- MAC VENDOR ---------------------------------------------- #

    # Updates the mac vendor field of all devices in the current network's table of the database
    def add_mac_vendors(self, network, lb):

        # Adds mac vendor to device and saves to database
        for device in network.devices.values():
            device.mac_vendor = self.mac_table.find_vendor(device.mac)
            lb.increment()

    # ---------------------------------------------- ARP SCANNING ---------------------------------------------- #

    # Sends an ARP ping to the given ip address to check it is alive and retrieve its MAC
    def arp_helper(self, ip, iface):

        # Creating ARP packet
        arp_frame = ARP(pdst=ip)
        ethernet_frame = Ether(dst="FF:FF:FF:FF:FF:FF")
        request = ethernet_frame / arp_frame

        # Send/recieve packet
        response = srp1(request, iface=iface, timeout=0.5, retry=2, verbose=False)

        # Formulate return values
        found_ip = None
        found_mac = None

        if response:
            found_ip = response[0][1].psrc
            found_mac = response[0][1].hwsrc

        return found_ip, found_mac


    # Gets all active active devices on the network
    def add_devices(self, network, lb, iface=conf.iface):

        lb.state = "RUNNING"

        # Breaks subnet and gateway ip into bytes
        sm_split = network.dhcp_server_info["subnet_mask"].split(".")
        gateway_split = network.dhcp_server_info["router"].split(".")
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

        lb.set_total(num_addrs)

        # Preparing thread job parameters
        mutex = threading.Lock()
        cond = threading.Condition(lock=mutex)
        counter_ptr = [0]
        returns = [-1] * num_addrs

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
                            fptr=self.arp_helper,
                            args=(ip, iface,),
                            ret_ls=returns,
                            ret_id=job_counter,
                            counter_ptr=counter_ptr,
                            cond=cond,
                        )
                        job_counter += 1

                        if not self.threadpool.add_job(job):
                            return "Request size over maximum allowed size %d" % (self.threadpool.MAX_QUEUE_SIZE)

        # Waits for all tasks to be completed by the threadpool
        mutex.acquire()
        while counter_ptr[0] < num_addrs:
            cond.wait()
            lb.set_progress(counter_ptr[0])

        mutex.release()

        # Creates a device object for each ip and mac, saves to database
        for i in range(num_addrs):
            ip = returns[i][0]
            mac = returns[i][1]
            if mac and ip and mac not in network.devices.keys():
                network.devices[mac] = Device(ip, mac)

        lb.state = "DONE!"
        


    # ---------------------------------------------- TRACEROUTE ---------------------------------------------- #

    # Thread worker to get path to provided ip address
    def traceroute_helper(self, ip, gateway, iface):

        # Emits UDP packets with incrementing ttl until the target is reached
        answers = traceroute(ip, maxttl=10, iface=iface, verbose=False)[0]
        addrs = [gateway]

        # Responses return out of order so we reorder them by ttl
        hops = {}
        if ip in answers.get_trace().keys():
            for answer in answers.get_trace()[ip].keys():
                hops[answer] = answers.get_trace()[ip][answer][0]

        for hop in sorted(hops.keys()):
            if hops[hop] not in addrs:
                addrs.append(hops[hop])

        if addrs[-1] != ip:
            addrs.append(ip)

        return addrs


    # Runs a traceroute on all devices in the database to get their neighbours in the routing path, updates and saves to database
    def add_routes(self, network, lb, iface=conf.iface):

        # Retrieve network devices from database
        device_addrs = set()
        gateway = network.dhcp_server_info["router"]

        # Preparing thread job parameters
        mutex = threading.Lock()
        cond = threading.Condition(lock=mutex)
        counter_ptr = [0]
        returns = [-1] * len(network.devices.keys())

        # The current job, for referencing the return location for the thread
        job_counter = 0

        for device in network.devices.values():
            # Creates job and adds to threadpool queue for execution
            device_addrs.add(device.ip)
            job = Job(
                fptr=self.traceroute_helper,
                args=(device.ip, gateway, iface,),
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
        while counter_ptr[0] < len(network.devices.keys()):
            cond.wait()
            lb.set_progress(counter_ptr[0])

        mutex.release()

        to_add = []
        # Parses output
        job_counter = 0
        for device in network.devices.values():
            parent = gateway
            for addr in returns[job_counter]:
                # Adds devices if they don't already exist
                if addr not in device_addrs:
                    device_addrs.add(addr)
                    mac = self.arp_helper(addr, iface)[1]
                    new_device = Device(addr, mac)
                    new_device.parent = parent
                    to_add.append(new_device)

                if addr == device.ip:
                    break

                parent = addr

            # Updates the devices parent node
            device.parent = parent
            job_counter += 1

        for device in to_add:
            network.devices[device.mac] = device


    def vertical_traceroute(self, network, iface=conf.iface, target_host="8.8.8.8"):

        # Run traceroute to google's DNS server
        traceroute_results = self.traceroute_helper(target_host, network.dhcp_server_info["router"], iface)
        # Print the traceroute results
        for i in range(len(traceroute_results) - 1):
            ip = traceroute_results[i]
            if self.get_ip_class(ip) != None:

                mac = self.arp_helper(ip, iface)[1]
                if mac == None:
                    continue

                if mac in network.devices.keys():
                    network.devices[mac].parent = traceroute_results[i+1]
                    continue

                new_device = Device(ip, mac)
                new_device.parent = traceroute_results[i+1]
                network.devices[mac] = new_device
        

    # ---------------------------------------------- WEBSITE STATUS ---------------------------------------------- #

    # Checks if the requested ip is hosting a website or not
    def website_status_helper(self, ip):

        url = "http://%s" % (ip)
        try:
            response = requests.get(url, timeout=1)
            
            return 200 <= response.status_code < 300
        except requests.RequestException:
            return False 
        

    def dispatch_website_scan(self, network, attr):

        # The current job, for referencing the return location for the thread
        job_counter = 0
        for device in network.devices.values():
            # Create job and add to threadpool queue for execution
            job = Job(
                fptr=self.website_status_helper,
                args=(device.ip,),
                ret_ls=attr.ret,
                ret_id=job_counter,
                counter_ptr=attr.ctr,
                cond=attr.cond,
            )
            job_counter += 1

            if not self.threadpool.add_job(job):
                return "Request size over maximum allowed size %d" % (
                    self.threadpool.MAX_QUEUE_SIZE
                )


    
    def update_website_status(self, network, ret):
        # Sets all devices websites
        job_id = 0
        for device in network.devices.values():
            if ret[job_id]:
                device.website = "http://%s" % device.ip
            else:
                device.website = "Not Hosted"
            job_id += 1

        
    # ---------------------------------------------- OS FINGERPRINTING ---------------------------------------------- #


    # Thread worker to get os info from the provided ip address
    def os_helper(self, ip):

        nm = nmap3.Nmap()

        os_info = {"os_type": "unknown", "os_vendor": "unknown", "os_family": "unknown"}
        try:
            # Performs scan
            data = nm.nmap_os_detection(ip, args="--script-timeout 20 --host-timeout 20")
        except:
            return os_info

        # Parses output for os info
        if ip in data.keys():
            if "osmatch" in data[ip] and len(data[ip]["osmatch"]) > 0:
                osmatch = data[ip]["osmatch"][0]
                if "osclass" in osmatch:
                    osclass = osmatch["osclass"]

                    os_info["os_type"] = osclass["type"]
                    os_info["os_vendor"] = osclass["vendor"]
                    os_info["os_family"] = osclass["osfamily"]

        return os_info


    def dispatch_os_scan(self, network, attr, iface=conf.iface):

        # The current job, for referencing the return location for the thread
        job_counter = 0
        for device in network.devices.values():
            # Create job and add to threadpool queue for execution
            job = Job(
                fptr=self.os_helper,
                args=(device.ip,),
                ret_ls=attr.ret,
                ret_id=job_counter,
                counter_ptr=attr.ctr,
                cond=attr.cond,
            )
            job_counter += 1

            if not self.threadpool.add_job(job):
                return "Request size over maximum allowed size %d" % (
                    self.threadpool.MAX_QUEUE_SIZE
                )
            

    def update_os(self, network, ret):
        # Sets all devices OS information
        job_id = 0
        for device in network.devices.values():
            device.os_type = ret[job_id]["os_type"]
            device.os_family = ret[job_id]["os_family"]
            device.os_vendor = ret[job_id]["os_vendor"]
            job_id += 1


    # ---------------------------------------------- HOSTNAME LOOKUP ---------------------------------------------- #


    # Thread worker for reverse DNS lookup
    def hostname_helper(self, addr):

        try:
            return socket.gethostbyaddr(addr)[0]
        except:
            return "unknown"


    # Retrieves the hostnames of all devices on the network and saves them to the database
    def dispatch_hostname_scan(self, network, attr):

        # The current job, for referencing the return location for the thread
        job_counter = 0
        for device in network.devices.values():

            # Create job and add to threadpool queue for execution
            job = Job(
                fptr=self.hostname_helper,
                args=(device.ip,),
                ret_ls=attr.ret,
                ret_id=job_counter,
                counter_ptr=attr.ctr,
                cond=attr.cond,
            )
            job_counter += 1

            if not self.threadpool.add_job(job):
                return "Request size over maximum allowed size %d" % (
                    self.threadpool.MAX_QUEUE_SIZE
                )


    def update_hostnames(self, network, ret):
        # Add returned hostnames to devices, save to database
        job_counter = 0
        for device in network.devices.values():
            if ret[job_counter] != "unkown":
                device.hostname = ret[job_counter]
            job_counter += 1


    # ---------------------------------------------- DHCP INFO ---------------------------------------------- #


    # Gets the gateway, interface, subnet mask and domain name of the current network
    def get_dhcp_server_info(self, ):

        gws = netifaces.gateways()

        # Failsafe defaults in the event that there is no network connection
        default_gateway = None
        default_iface = "unknown"
        subnet_mask = "255.255.255.0"
        domain = "unknown"

        if "default" in gws.keys() and netifaces.AF_INET in gws["default"].keys():
            default_gateway = netifaces.gateways()["default"][netifaces.AF_INET][0]
            default_iface = netifaces.gateways()["default"][netifaces.AF_INET][1]
            subnet_mask = netifaces.ifaddresses(default_iface)[netifaces.AF_INET][0][
                "netmask"
            ]
            domain = self.hostname_helper(default_gateway)

        return {
            "router": default_gateway,
            "iface": default_iface,
            "subnet_mask": subnet_mask,
            "domain": domain,
        }


    def get_gateway_mac(self, iface=conf.iface):

        dhcp_info = self.get_dhcp_server_info()
        return self.arp_helper(dhcp_info["router"], iface)[1]


    # ---------------------------------------- IP ----------------------------------------------------- #


    def get_ip_class(self, ip):

        def ip_val(ip):

            val = 0
            exp = 0

            for i in ip.split(".")[::-1]:
                val += int(i) * pow(256, exp)
                exp += 1
            return val
        
        ip = ip_val(ip)

        if ip >= ip_val("10.0.0.0") and ip <= ip_val("10.255.255.255"):
            return "A"
        
        if ip >= ip_val("172.16.0.0") and ip <= ip_val("172.31.255.255"):
            return "B"

        if ip >= ip_val("192.168.0.0") and ip <= ip_val("192.168.255.255"):
            return "C"
        
        return None


    # ---------------------------------------- PORTS ---------------------------------------------------- #


    def ports_helper(self, ip, iface, ports):

        out = []
        idx = 0

        for port in ports:
            try:
                # Create a TCP SYN packet to check if the port is open
                response = sr1(IP(dst=ip) / TCP(dport=port, flags="S"), timeout=1, iface=iface, verbose=False)

                if response and response.haslayer(TCP):
                    # TCP SYN-ACK flag
                    if response.getlayer(TCP).flags == 0x12:  
                        out.append(port)
            except Exception as e:
                print(f"An error occurred: {str(e)}")

            idx += 1
        return out


    def dispatch_port_scan(self, network, ports, attr, iface=conf.iface):

        if ports == []:
            return
    
        # The current job, for referencing the return location for the thread
        job_counter = 0
        for device in network.devices.values():

            # Create job and add to threadpool queue for execution
            job = Job(
                fptr=self.ports_helper,
                args=(device.ip, iface, ports,),
                ret_ls=attr.ret,
                ret_id=job_counter,
                counter_ptr=attr.ctr,
                cond=attr.cond,
            )
            job_counter += 1

            if not self.threadpool.add_job(job):
                return "Request size over maximum allowed size %d" % (self.threadpool.MAX_QUEUE_SIZE)


    def update_ports(self, network, ret):
        # Add returned hostnames to devices, save to database
        job_counter = 0
        for device in network.devices.values():
            ports_open = []
            for port in ret[job_counter]:
                ports_open.append(port)

            device.ports = ports_open
            job_counter += 1