class Device:

    default = "unknown"
    
    ip = default
    mac = default
    mac_vendor = default
    os_family = default
    os_vendor = default
    os_type = default
    hostname = default
    parent = default
    ports = []

    # Required not null fields
    def __init__(self, ip, mac):
        self.ip = ip
        self.mac = mac

    def to_json(self):

        port_str = "".join(str(x) + "," for x in self.ports)[:-1]
        return {"mac" : self.mac, 
                "ip" : self.ip, 
                "mac_vendor" : self.mac_vendor, 
                "os_family" : self.os_family, 
                "os_vendor" : self.os_vendor, 
                "os_type" : self.os_type, 
                "hostname" : self.hostname, 
                "parent" : self.parent, 
                "ports" : port_str}