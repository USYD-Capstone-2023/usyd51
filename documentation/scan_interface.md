# scan_interface.py Documentation #

## Settings ##

There is a settings file stored at ```src/scanning/settings.json```, that dictates the specific behaviour of each scan, namely which scans are run and what paramters are used. In the event that the settings file becomes malformed or invalid, it will be substituted with the default one seen below:
```json
{
    "TCP":true,
    "UDP":true, 
    "ports": [22,23,80,443],

    "run_ports": false,
    "run_os": false,
    "run_hostname": true,
    "run_mac_vendor": true,
    "run_trace": true,
    "run_vertical_trace": true,

    "defaultView": "grid",
    "defaultNodeColour": "0FF54A",
    "defaultEdgeColour": "32FFAB",
    "defaultBackgroundColour": "320000"
}
```

## Scan Network ##

### Description ###

Runs the scans specified in the settings file, currently including support for:
- ARP
- Traceroute
- Vertical Traceroute (Find local connections between the gateway and the web)
- Mac Vendor Resolution
- Hostname Reverse Lookup
- OS Fingerprinting
- Port Scanning

The results of these scans are sent to the database server to be stored.

There is an optional *network_id* parameter, which can be given to indicate that the network already exists, adding to the database entry for that network if that is the case. If no ID is given or an incorrect ID is given, the database will assign the network a new unique ID.

### Usage ###

```bash
python3 scan_interface.py scan_network [network_id]
```

## Get Current SSID ##

### Description ###

Retrieves the SSID of the network that the user is currently connected to from either the kernel or a scan (os dependent).

### Usage ###

```bash
python3 scan_interface.py ssid
```

### Return Format ###

Currently just prints SSID, need to use FIFOs or similar to communicate the result to Node.
```json
<SSID>
```

## Get DHCP Server Info ##

### Description ###

Retrieves the DHCP server information for the current network.

### Usage ###

```bash
python3 scan_interface.py dhcp
```

### Return Format ###

Currently just prints, need to use FIFOs or similar to communicate the result to Node.

```json
{
    "router"     : default gateway's IP address,
    "iface"      : default interface,
    "subnet_mask": network's subnet mask,
    "domain"     : domain name,
}
```