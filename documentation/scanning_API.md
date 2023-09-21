# scan_interface.py Documentation #

## Settings ##

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

The behaviour of the ```/scan/``` feature is dependent on the user's settings in the database, which determines which scans are run and what paramters are used. 

There is an optional *network_id* parameter, which can be given to indicate that the network already exists, adding to the database entry for that network if that is the case. If no ID is given or an incorrect ID is given, the database will assign the network a new unique ID.

### Usage ###

```json
"GET /scan/<network_id>"
```

If network_id == -1 or a value that isnt in the database, scans and creates a new network in the database, with a uniquely assigned ID.
If the network_id is in the database, adds the current scan as a snapshot in its history.

## Get Current SSID ##

### Description ###

Retrieves the SSID of the network that the user is currently connected to from either the kernel or a scan (os dependent).

### Usage ###

```json
"GET /ssid"
```

### Return Format ###

```json
<SSID>
```

## Get DHCP Server Info ##

### Description ###

Retrieves the DHCP server information for the current network.

### Usage ###

```bash
"GET /dhcp"
```

### Return Format ###

```json
{
    "router"     : default gateway's IP address,
    "iface"      : default interface,
    "subnet_mask": network's subnet mask,
    "domain"     : domain name,
}
```