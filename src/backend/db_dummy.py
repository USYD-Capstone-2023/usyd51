class db_dummy:

    # network {mac : {mac : device}}
    devices = {}
    networks = {}
    def __init__(self, database, username, password, host="localhost", port="5432"):
        self.connection = None
        self.cursor = None

        self.db = database
        self.un = username
        self.ps = password

        self.host = host
        self.port = port

    def contains_mac(self, mac, network_id):
        if network_id in self.devices.keys():
            return mac in self.devices[network_id].keys()

        return false

    def add_attribute(self, attr, val, network_id, mac):
        print(self.devices)
        self.devices[network_id][mac][attr] = val
        print(self.devices)

    def register_network(self, network_id):
        if network_id not in self.devices.keys():
            self.devices[network_id] = {}

    def get_all_devices(self, network_id):
        return self.devices[network_id]

    def add_device(self, device, network_id):
        self.devices[network_id][device.mac] = device

    def add_device_route(self, device, network_id, route):
        self.devices[network_id][device.mac].route = route
