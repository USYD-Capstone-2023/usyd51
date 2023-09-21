# API Spec #

This reference sheet demonstrates the usage and return formats of all endpoints used in the flask database server found at ```/src/backend/app.py```. If running locally, this system can be run with ```sudo flask run``` granted that postgreSQL is setup on your system.

## Network Information ##

### Description ###

Retrieves the basic, defining information of a specific network from the database.

### Usage ###
```python
"GET /networks/<network_id>"
```

### Return Format ##

```json
{
    "id"          : unique network id,
    "gateway_mac" : MAC address of the network's gateway,
    "name"        : the network's human name,
    "ssid"        : the network's SSID
} 
```

or 

```json
"Network with ID %d is not present in the database.", 500

If an error has occurred
```

## Network Devices ##

### Description ###

Retrieves all devices associated with a network from the most recent scan in the database.

### Usage ###
```python
"GET /networks/<network_id>/devices"
```

### Return Format ###

```json
[
    {
        "mac"        : the device's MAC address, 
        "ip"         : the device's IP address, 
        "mac_vendor" : the vendor that produced the device's network interface, 
        "os_family"  : the family of operating systems the device belongs to, 
        "os_vendor"  : the manufacturer of the device's OS, 
        "os_type"    : the type of OS the device runs, 
        "hostname"   : the device's name, 
        "parent"     : the IP of the device's parent node in the routing tree, 
        "ports"      : the ports that are scanned and open on the device
    }, ...
]

```

or

```json
"Network with ID %d is not present in the database.", 500

If an error has occurred
```

## Add a Network ##

### Description ###

Allows users to add a device into the database. If the request is sent with an invalid ID number, a unique one is assigned by the database. If the request is sent with an ID that is present in the database, it will be added to that network's history. This endpoint should be used exclusively by the scanning utilities found at ```/src/scanning/scan_interface.py```.

### Usage ###
```json
"PUT /networks/add"
json = 
{
    "network_id"  : unique network id,
    "gateway_mac" : MAC address of the network's gateway,
    "name"        : the network's human name,
    "ssid"        : the network's SSID,
    "timestamp"   : the time the scan was taken,
    "devices"     : [
                    {
                        "mac"        : the device's MAC address, 
                        "ip"         : the device's IP address, 
                        "mac_vendor" : the vendor that produced the device's network interface, 
                        "os_family"  : the family of operating systems the device belongs to, 
                        "os_vendor"  : the manufacturer of the device's OS, 
                        "os_type"    : the type of OS the device runs, 
                        "hostname"   : the device's name, 
                        "parent"     : the IP of the device's parent node in the routing tree, 
                        "ports"      : the ports that are scanned and open on the device
                    }, ...
                    ]
}
```

### Return Format ###

```json
"Success", 200

or

"Database encountered an error registering new network", 500

or

"Database encountered an error saving devices", 500
```

## Update Existing Network ##

### Description ###

Updates the devices associated with the most recent scan on the given network, without creating a new scan snapshot. This is used when running different scans at different times, so that we can have, for example os information scanned in the background and added as required.

### Usage ###

```json
"PUT /networks/<network_id>/update"
json = 
{
    "network_id"  : unique network id,
    "devices"     : [
                    {
                        "mac"        : the device's MAC address, 
                        "ip"         : the device's IP address, 
                        "mac_vendor" : the vendor that produced the device's network interface, 
                        "os_family"  : the family of operating systems the device belongs to, 
                        "os_vendor"  : the manufacturer of the device's OS, 
                        "os_type"    : the type of OS the device runs, 
                        "hostname"   : the device's name, 
                        "parent"     : the IP of the device's parent node in the routing tree, 
                        "ports"      : the ports that are scanned and open on the device
                    }, ...
                    ]
}
```

### Return Format ###

```json
"Success", 200

or

"No network with ID %d exists in database.", 500

or

"Malformed network.", 500

or 

"Database encountered an error saving devices", 500
```

## Get Network DHCP Info ##

### Description ###

Used to retrieve the DHCP server information of the desired network from the database. THIS IS CURRENTLY NOT USED OR IMPLEMENTED PROPERLY, WILL IMPLEMENT IF REQUIRED.

### Usage ###
```json
"GET /networks/<network_id>/dhcp"
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

## Get All Networks' Info ##

### Description ###

Retrieves the basic, defining information about all networks currently stored in the database. Used to create menus showing all networks.

### Usage ###
```json
GET "/networks"
```

### Return Format ###

```json
[

    {
        "id"          : unique network id,
        "gateway_mac" : MAC address of the network's gateway,
        "name"        : the network's human name,
        "ssid"        : the network's SSID
    }, ...
]
```

## Rename a Network ##

### Description ###

Allows renaming of an existing network and its associated data. 
AT THE MINUTE THIS IS IMPLEMENTED AS A *GET* REQUEST FOR EASE OF TESTING, WILL BE A PUT REQUEST ONCE THE FRONTEND IS IMPLEMENTED.

### Usage ###
```json
GET "/networks/<network_id>/rename/<new_name>"
```

### Return Format ###

```json
"Success", 200

or

"Network with id %d not present in database.", 500
```

## Delete a Network ##

### Description ###

Allows the deletion of a network corresponding to its unique ID number.
AT THE MINUTE THIS IS IMPLEMENTED AS A *GET* REQUEST FOR EASE OF TESTING, WILL BE A PUT REQUEST ONCE THE FRONTEND IS IMPLEMENTED.

### Usage ###
```json
"/networks/<network_id>/delete"
```

### Return Format ###

```json
"Success", 200

or

"Network with id %d not present in database." % (network_id), 500
```

## Get Settings ##

### Description ###

Gets the JSON string of the settings selected and saved for the current user.

### Usage ###

```json
"GET /settings/<user_id>"
```

### Return Format ###

```json
{
    "user_id" : (int) user ID,
    "TCP" : (bool)Run TCP port scans?,
    "UDP" : (bool) Run UDP port scans?,
    "ports" : (string) "[ports, to, scan]",
    "run_ports" : (bool) Run port scan?,
    "run_os" : (bool) Run OS scan?,
    "run_hostname" : (bool) Run hostname lookup?,
    "run_mac_vendor" : (bool) Run mac vendor lookup?,
    "run_trace" : (bool) Run traceroute?,
    "run_vertical_trace" : (bool) Run vertical traceroute?,
    "defaultView" : (string) View style,
    "defaultNodeColour" : (string) Node colour,
    "defaultEdgeColour" : (string) edge colour,
    "defaultBackgroundColour" : (string) background colour
}
```

## Update/Set Settings ##

### Description ###

Sets the user's scan settings and UI preferences.

### Usage ###

```json
"PUT /settings/<user_id>/set"
json={
    "TCP" : (bool)Run TCP port scans?,
    "UDP" : (bool) Run UDP port scans?,
    "ports" : (string) "[ports, to, scan]",
    "run_ports" : (bool) Run port scan?,
    "run_os" : (bool) Run OS scan?,
    "run_hostname" : (bool) Run hostname lookup?,
    "run_mac_vendor" : (bool) Run mac vendor lookup?,
    "run_trace" : (bool) Run traceroute?,
    "run_vertical_trace" : (bool) Run vertical traceroute?,
    "defaultView" : (string) View style,
    "defaultNodeColour" : (string) Node colour,
    "defaultEdgeColour" : (string) edge colour,
    "defaultBackgroundColour" : (string) background colour
    }
```

### Return Format ###

```json
"Malformed settings file.", 500

or

"Database error.", 500

or

"Success", 200
```