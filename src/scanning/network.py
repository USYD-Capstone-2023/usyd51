class Network:

    # { mac : device }
    devices = {}

    def __init__(self, ssid, timestamp, dhcp_server_info, network_id):

        self.ssid = ssid
        self.timestamp = timestamp
        self.network_id = network_id
        self.dhcp_server_info = dhcp_server_info

    def add_device(self, device):

        if device:
            self.devices[device.mac] = device
    

    def to_json(self):

        out = {}

        out["network_id"] = self.network_id 
        out["ssid"] =  self.ssid
        out["timestamp"] = self.timestamp
        out["devices"] = {d.mac : d.to_json() for d in self.devices.values()}

        return out

    

        