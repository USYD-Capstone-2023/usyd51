class Client:

    # os_info
    os_type = "unknown"
    os_vendor = "unknown"
    os_family = "unknown"

    # host_info
    ip = "unknown"
    hostname = "unknown"

    # mac_info
    mac = "unknown"
    mac_vendor = "unknown"

    # distance from gateway
    layer_level = -1
    parent = ""

    def __init__(self):
        self.neighbours = set()

    def add_host_info(self, ip, hostname, mac, mac_vendor):
        self.ip = ip
        self.hostname = hostname
        self.mac = mac
        self.mac_vendor = mac_vendor

    def add_os_info(self, os_type, os_vendor, os_family):
        self.os_type = os_type
        self.os_vendor = os_vendor
        self.os_family = os_family

    def add_neighbour(self, client):
        if client not in self.neighbours:
            self.neighbours.add(client)

    def to_map(self):

        out = {"name" : self.hostname, "mac" : self.mac, "mac_vendor" : self.mac_vendor, "os_type" : self.os_type,
                "os_vendor" : self.os_vendor, "os_family" : self.os_family, "neighbours" : [x.hostname for x in self.neighbours],
                "layer_level" : self.layer_level, "parent" : self.parent}

        return out