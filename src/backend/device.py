class Device:

    ip = "unknown"
    mac = "unknown"
    mac_vendor = "unknown"
    os_family = "unknown"
    os_vendor = "unknown"
    os_type = "unknown"
    hostname = "unknown"
    route = []

    # Required not null fields
    def __init__(self, ip, mac):
        self.ip = ip
        self.mac = mac

    def to_json(self):
        return {"mac" : self.mac, "ip" : self.ip, "mac_vendor" : self.mac_vendor, "os_family" : self.os_family, "os_vendor" : self.os_vendor, "os_type" : self.os_type, "hostname" : self.hostname, "route" : self.route}