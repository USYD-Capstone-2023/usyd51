# scan_interface.py Documentation #

The scan interface is run as a server that can be located either locally, or remotely on another network.
It can be run in either "local" or "remote" mode, where local means that the database server is being served on "127.0.0.1:5000", and remote means the server is located at "192.168.12.104:5000" (Access with wireguard).

Either mode can be run as:

```bash
sudo python3 scan_interface.py local
```

or

```bash
sudo python3 scan_interface.py remote
```

## Settings ##

Each user in the database has a collection of settings associated with them to dictate the behaviour of scans, and some frontend preferences. In the event that the settings file becomes malformed or invalid, it will be substituted with the default one seen below:
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

The default settings are also given to new users.

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

```json
"POST /scan/<network_id>"
headers={"Auth-Token" : The user's authentication token}
```

### Return Format ###

If no authentication token is supplied:

```json
"Authentication token not in request headers.", 401
```

If an invalid authentication token is supplied, or the token doesnt grant required access:

```json
"Current user does not have access to this resource.", 401
"Authentication token not in request headers.", 401
"No user ID contained in authentication token.", 401
"Malformed auth token.", 401
"Token has expired, login again", 401
"User doesn't exist.", 401
"Invalid authentication token.", 401
```
as appropriate.

If the network ID is invalid (i.e. not a positive integer):

```json
"Invalid network ID entered.", 500
```

If there is a failure in the settings system (this shouldnt occur, and only happens if the database fumbles the settings even after a settings reset):

```json
"Malformed settings, automatic reset has failed. Please contact system administrator.", 500
```

### Post Conditions ###

- If the authentication token and network format are valid, the network will be added into the database under the user's name to be accessed later.
- If the network was given with an ID of -1, it will be given the next available ID by the database.
- If the network was given with an ID that is already taken by the current network, it will be added as a snapshot for that network.
- If the network was given with an ID that isnt taken, it will be stored under that ID.
- The system will give a HTTP 401 Unauthorized if the user attempts to save a network to a network ID that is held by another user.

## Get Current SSID ##

### Description ###

Retrieves the SSID of the network that the user is currently connected to from either the kernel or a scan (os dependent).

### Usage ###

```json
"GET /ssid"
```

### Return Format ###

```json
SSID, 200
```

## Get DHCP Server Info ##

### Description ###

Retrieves the DHCP server information for the current network.

### Usage ###

```json
"GET /dhcp"
```

### Return Format ###

```json
{
    "router"     : default gateway's IP address,
    "iface"      : default interface,
    "subnet_mask": network's subnet mask,
    "domain"     : domain name,
}, 200
```