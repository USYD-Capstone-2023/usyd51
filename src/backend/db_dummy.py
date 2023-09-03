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

        return False

    def save_device(self, device, network_id):
        if device.mac in self.devices[network_id].keys():
            self.devices[network_id][device.mac] = device
            
        self.devices[network_id][device.mac] = device

    def get_device(self, network_id, mac):
        return self.devices[network_id][mac]

    def register_network(self, network_id):
        if network_id not in self.devices.keys():
            self.devices[network_id] = {}

    def get_all_devices(self, network_id):
        return self.devices[network_id]

    def add_device(self, device, network_id):
        self.devices[network_id][device.mac] = device

    def add_device_parent(self, device, network_id, parent):
        self.devices[network_id][device.mac].parent = parent
