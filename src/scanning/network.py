class Network:

    # { mac : device }
    devices = {}

    def __init__(self, ssid, name, timestamp, dhcp_server_info, gateway_mac, network_id):

        self.ssid = ssid
        self.name = name
        self.timestamp = timestamp
        self.network_id = network_id
        self.gateway_mac = gateway_mac
        self.dhcp_server_info = dhcp_server_info


    def add_device(self, device):

        if device:
            self.devices[device.mac] = device
    

    def to_json(self):

        out = {}

        out["network_id"] = self.network_id 
        out["ssid"] =  self.ssid
        out["name"] = self.name
        out["gateway_mac"] = self.gateway_mac
        out["timestamp"] = self.timestamp
        out["devices"] = {d.mac : d.to_json() for d in self.devices.values()}

        return out

    

        