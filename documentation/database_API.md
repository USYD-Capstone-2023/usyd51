# API Spec #

This reference sheet demonstrates the usage and return formats of all endpoints used in the flask database server found at ```/src/backend/database_server.py```. If running locally, this system can be run with ```json3 database_server local``` granted that postgreSQL is setup on your system, or using the remote server option ```json3 database_server remote```.

## Sign Up ##

### Description ###

Registers a new user into the database, where their username is the unique identifier.

### Usage ###

```json
"POST /signup"
json = 
{
    "username" : Then user's unique username,
    "password" : The hash of the user's password,
    "email"    : The user's email address
}
```


### Return Format ###

If a user already exists with the given username, the server responds with:

```json
"A user with that username already exists.", 507
```

If an error occurs:

```json
"The database server encountered an error, please try again.", 508
```

or if successful:

```json
"Success.", 200
```

## Login ##

### Description ###

Logs a user into their account, giving them an authentication token that can be used to access their data on the database server.

### Usage ###

```json
"POST /login"
json = 
{
    "username" : Then user's unique username,
    "password" : The hash of the user's password,
}
```

### Return Format ###

If an error occurs, or the user's credentials are invalid:

```json
"specific error message", 401
```

If successful:
```json
authToken, 200
```

## Get All Networks' Info ##

### Description ###

Retrieves the basic, defining information about all networks currently stored in the database. Used to create menus showing all networks.

### Usage ###
```json
GET "/networks"
headers={"Auth-Token" : User's auth token}
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

## Network Information ##

### Description ###

Retrieves the basic, defining information of a specific network from the database.

### Usage ###
```json
"GET /networks/<network_id>"
headers={"Auth-Token" : User's auth token}
```

### Return Format ##

```json
{
    "id"          : unique network id,
    "gateway_mac" : MAC address of the network's gateway,
    "name"        : the network's human name,
    "ssid"        : the network's SSID
}, 200
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
```json
"GET /networks/<network_id>/devices"
headers={"Auth-Token" : User's auth token}
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
], 200

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
headers={"Auth-Token" : User's auth token}
json = 
{
    "network_id"  : (int)    unique network id,
    "gateway_mac" : (string) MAC address of the network's gateway,
    "name"        : (string) the network's human name,
    "ssid"        : (string) the network's SSID,
    "timestamp"   : (int) the time the scan was taken,
    "devices"     : {
        (string) device's mac :
                    {
                        "mac"        : (string) the device's MAC address, 
                        "ip"         : (string) the device's IP address, 
                        "mac_vendor" : (string) the vendor that produced the device's network interface, 
                        "os_family"  : (string) the family of operating systems the device belongs to, 
                        "os_vendor"  : (string) the manufacturer of the device's OS, 
                        "os_type"    : (string) the type of OS the device runs, 
                        "hostname"   : (string) the device's name, 
                        "parent"     : (string) the IP of the device's parent node in the routing tree, 
                        "ports"      : (list)   the ports that are scanned and open on the device
                    }, ...
                    }                 
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
headers={"Auth-Token" : User's auth token}
json = 
{
    "network_id"  : unique network id,
    "devices"     : {
        (string) device's mac :
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
                    }   
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
headers={"Auth-Token" : User's auth token}
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


## Rename a Network ##

### Description ###

Allows renaming of an existing network and its associated data. 

### Usage ###
```json
PUT "/networks/<network_id>/rename/<new_name>"
headers={"Auth-Token" : User's auth token}
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

### Usage ###
```json
POST "/networks/<network_id>/delete"
headers={"Auth-Token" : User's auth token}
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
"GET /settings"
headers={"Auth-Token" : User's auth token}
```

### Return Format ###

```json
{
    "user_id"                 : (int)    The user's id number,
    "TCP"                     : (bool)   Run TCP port scans?,
    "UDP"                     : (bool)   Run UDP port scans?,
    "ports"                   : (string) "[ports, to, scan]",
    "run_ports"               : (bool)   Run port scan?,
    "run_os"                  : (bool)   Run OS scan?,
    "run_hostname"            : (bool)   Run hostname lookup?,
    "run_mac_vendor"          : (bool)   Run mac vendor lookup?,
    "run_trace"               : (bool)   Run traceroute?,
    "run_vertical_trace"      : (bool)   Run vertical traceroute?,
    "defaultView"             : (string) View style,
    "defaultNodeColour"       : (string) Node colour,
    "defaultEdgeColour"       : (string) edge colour,
    "defaultBackgroundColour" : (string) background colour
}, 200
```

or 

```json
"no_user" : ("User with given ID is not present in the database.", 502),
"malformed_settings" : ("Provided settings information is malformed.", 504),
"db_error" : ("The database server encountered an error, please try again.", 508)
```

as appropriate.

## Update/Set Settings ##

### Description ###

Sets the user's scan settings and UI preferences.

### Usage ###

```json
"PUT /settings/set"
headers={"Auth-Token" : User's auth token}
json={
    "user_id"                 : (int)    The user's id number,
    "TCP"                     : (bool)   Run TCP port scans?,
    "UDP"                     : (bool)   Run UDP port scans?,
    "ports"                   : (string) "[ports, to, scan]",
    "run_ports"               : (bool)   Run port scan?,
    "run_os"                  : (bool)   Run OS scan?,
    "run_hostname"            : (bool)   Run hostname lookup?,
    "run_mac_vendor"          : (bool)   Run mac vendor lookup?,
    "run_trace"               : (bool)   Run traceroute?,
    "run_vertical_trace"      : (bool)   Run vertical traceroute?,
    "defaultView"             : (string) View style,
    "defaultNodeColour"       : (string) Node colour,
    "defaultEdgeColour"       : (string) edge colour,
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