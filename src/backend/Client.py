class Client:

    def __init__(self, ip, name, mac, vendor):
        self.ip = ip
        self.name = name
        self.mac = mac
        self.vendor = vendor
        self.neighbours = set()