# API Spec #

This reference sheet demonstrates the usage and return formats of all endpoints used in the flask database server found at ```/src/backend/database_server.py```. If running locally, this system can be run with ```python3 database_server local``` granted that postgreSQL is setup on your system, or using the remote server option ```python3 database_server remote```. The server is also available as a self contained docker container, and can be setup with ```sudo docker compose up -d``` in ```/src/backend```.

# Authentication #

Most endpoints are protected, and require an authentication token to be present in the headers of the request. This authentication token is granted to the client when they successfully login through the `/login` endpoint. When accessing a protected endpoint, the possible outputs are:

```json
{
    "message" : "Current user does not have access to this resource.",
        or
    "message" : "Provided authentication token is malformed.",
        or
    "message" : "Provided authentication token has expired.",
        or
    "message" : "No authentication token provided.",

    "status"  : 401,
    "content" : ""
}
```

as necessary.

## Sign Up ##
Authentication: Not Required
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
{
    "message" : "A user with that username already exists.",
        or
    "message" : "The database server encountered an error, please try again.",
        or
    "message" : "Bad request.",
        or
    "message" : "Provided user information is malformed.",
        or
    "message" : "Provided settings information is malformed.",

    "status"  : 500,
    "content" : ""
}
```

or if successful:
```json
{
    "message" : "Success.",
    "status"  : 200,
    "content" : ""
}
```

## Login ##
Authentication: Not Required

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
{
    "message" : "Bad request.",
        or
    "message" : "Provided user information is malformed.",
        or
    "message" : "The database server encountered an error, please try again.",

    "status"  : 500,
    "content" : ""
}
```

If successful:
```json
{
    "message" : "Success",
    "status"  : 200,
    "content" : {"Auth-Token" : token}
}
```

## Get All Networks' Info ##
Authentication: Required

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
```json
{
    "message" : "Success.",
    "status"  : 200,
    "content" : {
        "id"          : unique network id,
        "gateway_mac" : MAC address of the network's gateway,
        "name"        : the network's human name,
        "ssid"        : the network's SSID,
        "n_alive"     : number of devices online in last scan
        }
}
```

or 

```json
{
    "message" : "Bad request.",
        or
    "message" : "The database server encountered an error, please try again.",

    "status"  : 500,
    "content" : ""
}
```

## Network Information ##
Authentication: Required

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
    "message" : "Success.",
    "status"  : 200,
    "content" : {
        "id"          : unique network id,
        "gateway_mac" : MAC address of the network's gateway,
        "name"        : the network's human name,
        "ssid"        : the network's SSID,
        "n_alive"     : number of devices online in last scan
        }
}
```
or 

```json
{
    "message" : "Bad request.",
        or
    "message" : "The database server encountered an error, please try again.",
        or
    "message" : "Network with given ID is not present in the database.",

    "status"  : 500,
    "content" : ""
}
```
## Get Devices ##
Authentication: Required

### Description ###

Retrieves all devices associated with a network from the most recent scan in the database.

### Usage ###
```json
"GET /networks/<network_id>/devices"
headers={"Auth-Token" : User's auth token}
```

### Return Format ###

```json
{
    "message" : "Success.",
    "status"  : 200,
    "content" : {[
        {
            "mac"        : the device's MAC address, 
            "ip"         : the device's IP address, 
            "mac_vendor" : the vendor that produced the device's network interface, 
            "os_family"  : the family of operating systems the device belongs to, 
            "os_vendor"  : the manufacturer of the device's OS, 
            "os_type"    : the type of OS the device runs, 
            "hostname"   : the device's name, 
            "parent"     : the IP of the device's parent node in the routing tree, 
            "website"    : The address of the website being hosted by this device,
            "ports"      : the ports that are scanned and open on the device
        }, ...
    ]}
}
```
or 

```json
{
    "message" : "Bad request.",
        or
    "message" : "The database server encountered an error, please try again.",
        or
    "message" : "There is no snapshot of the given network taken at the given time.",
        or
    "message" : "Network with given ID is not present in the database.",

    "status"  : 500,
    "content" : ""
}
```

## Add a Network ##
Authentication: Required

### Description ###

Allows users to add a device into the database. If the request is sent with an invalid ID number, a unique one is assigned by the database. If the request is sent with an ID that is present in the database, it will be added to that network's history. This endpoint should be used exclusively by the scanning utilities found at ```/src/scanning/scan_interface.py```.

### Usage ###
```json
"PUT /networks/add"
headers={"Auth-Token" : User's auth token}
json = 
{
    "network_id"  : (int)    unique network id or -1 if user wants a new id to be assigned to the network,
    "gateway_mac" : (string) MAC address of the network's gateway,
    "name"        : (string) the network's human name,
    "ssid"        : (string) the network's SSID,
    "timestamp"   : (int)    the time the scan was taken,
    "devices"     : {string) device's mac :
                    {
                        "mac"        : (string) the device's MAC address, 
                        "ip"         : (string) the device's IP address, 
                        "mac_vendor" : (string) the vendor that produced the device's network interface, 
                        "os_family"  : (string) the family of operating systems the device belongs to, 
                        "os_vendor"  : (string) the manufacturer of the device's OS, 
                        "os_type"    : (string) the type of OS the device runs, 
                        "hostname"   : (string) the device's name, 
                        "parent"     : (string) the IP of the device's parent node in the routing tree, 
                        "website"    : (string) the address of the website being hosted by this device if hosting,
                        "ports"      : (list)   the ports that are scanned and open on the device
                    }, ...
                    }                 
}
```

### Return Format ###

```json
{
    "message" : "Success.",
    "status"  : 200,
    "content" : network_id
}
```
or

```json
{
    "message" : "Bad request.",
        or
    "message" : "The database server encountered an error, please try again.",
        or
    "message" : "Provided network information is malformed.",
        or 
    "message" : "Provided device information is malformed.",

    "status"  : 500,
    "content" : ""
}
```

## Update Existing Network ##
Authentication: Required

### Description ###

Updates the devices associated with the most recent scan on the given network, without creating a new scan snapshot. This is used when running different scans at different times, so that we can have, for example os information scanned in the background and added as required.

### Usage ###

```json
"PUT /networks/<network_id>/update"
headers={"Auth-Token" : User's auth token}
headers={"Auth-Token" : User's auth token}
json = 
{
    "network_id"  : (int)    unique network id or -1 if user wants a new id to be assigned to the network,
    "gateway_mac" : (string) MAC address of the network's gateway,
    "name"        : (string) the network's human name,
    "ssid"        : (string) the network's SSID,
    "timestamp"   : (int)    the time the scan was taken,
    "devices"     : {string) device's mac :
                    {
                        "mac"        : (string) the device's MAC address, 
                        "ip"         : (string) the device's IP address, 
                        "mac_vendor" : (string) the vendor that produced the device's network interface, 
                        "os_family"  : (string) the family of operating systems the device belongs to, 
                        "os_vendor"  : (string) the manufacturer of the device's OS, 
                        "os_type"    : (string) the type of OS the device runs, 
                        "hostname"   : (string) the device's name, 
                        "parent"     : (string) the IP of the device's parent node in the routing tree, 
                        "website"    : (string) the address of the website being hosted by this device if hosting,
                        "ports"      : (list)   the ports that are scanned and open on the device
                    }, ...
                    }                 
}
```

### Return Format ###

```json
{
    "message" : "Success.",
    "status"  : 200,
    "content" : network_id
}
```
or

```json
{
    "message" : "Bad request.",
        or
    "message" : "The database server encountered an error, please try again.",
        or
    "message" : "Network with given ID is not present in the database.",
        or
    "message" : "Provided network information is malformed.",
        or 
    "message" : "Provided device information is malformed.",

    "status"  : 500,
    "content" : ""
}
```


## Rename a Network ##
Authentication: Required

### Description ###

Allows renaming of an existing network and its associated data. 

### Usage ###
```json
PUT "/networks/<network_id>/rename/<new_name>"
headers={"Auth-Token" : User's auth token}
```

### Return Format ###

```json
{
    "message" : "Success.",
    "status"  : 200,
    "content" : ""
}
```

or

```json
{
    "message" : "Bad request.",
        or
    "message" : "The database server encountered an error, please try again.",
        or
    "message" : "Network with given ID is not present in the database.",

    "status"  : 500,
    "content" : ""
}
```

## Delete a Network ##
Authentication: Required

### Description ###

Allows the deletion of a network corresponding to its unique ID number.

### Usage ###
```json
POST "/networks/<network_id>/delete"
headers={"Auth-Token" : User's auth token}
```

### Return Format ###
```json
{
    "message" : "Success.",
    "status"  : 200,
    "content" : ""
}
```

or

```json
{
    "message" : "Bad request.",
        or
    "message" : "The database server encountered an error, please try again.",
        or
    "message" : "Network with given ID is not present in the database.",

    "status"  : 500,
    "content" : ""
}
```

## Get Network Snapshots ##
Authentication: Required

### Description ###

Gets a basic list of snapshots for the given network

### Usage ###

```json
POST "/networks/<network_id>/snapshots"
headers={"Auth-Token" : User's auth token}
```

### Return Format ###

```json
{
    "message" : "Success.",
    "status"  : 200,
    "content" : {[
        {
           "timestamp" : unix timestamp (seconds),
           "n_alive"   : Number of devices alive,
        }, ...
]}
}
```
or 

```json
{
    "message" : "Bad request.",
        or
    "message" : "The database server encountered an error, please try again.",
        or
    "message" : "Network with given ID is not present in the database.",

    "status"  : 500,
    "content" : ""
}
```

## Get Specific Network Snapshots ##
Authentication: Required

### Description ###

Gets all network and device information associated with the given snapshot and network id.

### Usage ###

```json
POST "/networks/<network_id>/snapshots/<timestamp>"
headers={"Auth-Token" : User's auth token}
```

### Return Format ###

```json
{
    "message" : "Success.",
    "status"  : 200,
    "content" : {[
        {
            "mac"        : the device's MAC address, 
            "ip"         : the device's IP address, 
            "mac_vendor" : the vendor that produced the device's network interface, 
            "os_family"  : the family of operating systems the device belongs to, 
            "os_vendor"  : the manufacturer of the device's OS, 
            "os_type"    : the type of OS the device runs, 
            "hostname"   : the device's name, 
            "parent"     : the IP of the device's parent node in the routing tree, 
            "website"    : The address of the website being hosted by this device,
            "ports"      : the ports that are scanned and open on the device
        }, ...
]}
}
```
or 

```json
{
    "message" : "Bad request.",
        or
    "message" : "The database server encountered an error, please try again.",
        or
    "message" : "There is no snapshot of the given network taken at the given time.",
        or
    "message" : "Network with given ID is not present in the database.",

    "status"  : 500,
    "content" : ""
}
```

## Share a Network ##
Authentication: Required

### Description ###

Allows a user to share a network that they have access to with another user.

### Usage ###

```json
POST "/networks/<network_id>/share/<recipient_id>"
headers={"Auth-Token" : User's auth token}
```

### Return Format ###

```json
{
    "message" : "Success.",
    "status"  : 500,
    "content" : ""
}
```

or

```json
{
    "message" : "Bad request.",
        or
    "message" : "The database server encountered an error, please try again.",
        or
    "message" : "Given user already has access to this network.",
        or
    "message" : "Network with given ID is not present in the database.",

    "status"  : 500,
    "content" : ""
}
```


## Get Users With Access ##
Authentication: Required

### Description ###

Returns a list of all users that have and dont have access to the given network.

### Usage ###

```json
POST "/users/<network_id>"
headers={"Auth-Token" : User's auth token}
```

### Return Format ###

```json
{
    "message" : "Success.",
    "status"  : 500,
    "content" : {
        "shared"   : [List of users with access],
        "unshared" : [List of users without access]
        }
}
```

or

```json
{
    "message" : "Bad request.",
        or
    "message" : "The database server encountered an error, please try again.",
        or
    "message" : "Network with given ID is not present in the database.",

    "status"  : 500,
    "content" : ""
}
```


## Get Salt ##
Authentication: Required

### Description ###

Retrieves the salt hashed with a given user's password.

### Usage ###

```json
POST "/users/<username>/salt"
headers={"Auth-Token" : User's auth token}
```

### Return Format ###

```json
{
    "message" : "Success.",
    "status"  : 200,
    "content" : {"salt" : salt}
}
```

or

```json
{
    "message" : "User with given ID is not present in the database.",
    "status"  : 500,
    "content" : ""
}
```


## Get Settings ##
Authentication: Required

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
    "message" : "Success.",
    "status"  : 200,
    "content" : {
        "user_id"                   : (str) The users id number,
        "TCP"                       : (bool) Run TCP port scans?,
        "UDP"                       : (bool) Run UDP port scans?,
        "ports"                     : (list) [ports, to, scan],
        "run_ports"                 : (bool) Run port scan?,
        "run_os"                    : (bool) Run OS scan?,
        "run_hostname"              : (bool) Run hostname lookup?,
        "run_mac_vendor"            : (bool) Run mac vendor lookup?,
        "run_website_status"        : (bool) Run website hosting check?,
        "run_vertical_trace"        : (bool) Run vertical traceroute?,
        "defaultView"               : (str)  Default visualisation style,
        "daemon_TCP"                : (bool) Run TCP port scans?,
        "daemon_UDP"                : (bool) Run UDP port scans?,
        "daemon_ports"              : (list) [ports, to, scan],
        "daemon_run_website_status" : (bool) Run website hosting check?,
        "daemon_run_ports"          : (bool) Run ports scan?,
        "daemon_run_os"             : (bool) Run OS scan?,
        "daemon_run_hostname"       : (bool) Run hostname lookup?,
        "daemon_run_mac_vendor"     : (bool) Run mac vendor lookup?,
        "daemon_run_vertical_trace" : (bool) Run vertical traceroute?,
        "daemon_scan_rate"          : (int) Daemon scanning interval (seconds),
        "scan_server_ip"            : (str) IP of scanning server (not implemented)
    }
}
```

or

```json
{
    "message" : "Bad request.",
        or
    "message" : "User with given ID is not present in the database.",
        or
    "message" : "Provided settings information is malformed.",
        or
    "message" : "The database server encountered an error, please try again.",

    "status"  : 500,
    "content" : ""
}
```

## Update/Set Settings ##
Authentication: Required

### Description ###

Sets the user's scan settings and UI preferences.

### Usage ###

```json
"PUT /settings/set"
headers={"Auth-Token" : User's auth token}
json={
        "TCP"                       : (bool) Run TCP port scans?,
        "UDP"                       : (bool) Run UDP port scans?,
        "ports"                     : (list) [ports, to, scan],
        "run_ports"                 : (bool) Run port scan?,
        "run_os"                    : (bool) Run OS scan?,
        "run_hostname"              : (bool) Run hostname lookup?,
        "run_mac_vendor"            : (bool) Run mac vendor lookup?,
        "run_website_status"        : (bool) Run website hosting check?,
        "run_vertical_trace"        : (bool) Run vertical traceroute?,
        "defaultView"               : (str)  Default visualisation style,
        "daemon_TCP"                : (bool) Run TCP port scans?,
        "daemon_UDP"                : (bool) Run UDP port scans?,
        "daemon_ports"              : (list) [ports, to, scan],
        "daemon_run_website_status" : (bool) Run website hosting check?,
        "daemon_run_ports"          : (bool) Run ports scan?,
        "daemon_run_os"             : (bool) Run OS scan?,
        "daemon_run_hostname"       : (bool) Run hostname lookup?,
        "daemon_run_mac_vendor"     : (bool) Run mac vendor lookup?,
        "daemon_run_vertical_trace" : (bool) Run vertical traceroute?,
        "daemon_scan_rate"          : (int) Daemon scanning interval (seconds),
        "scan_server_ip"            : (str) IP of scanning server (not implemented)
    }
```

### Return Format ###
```json
{
    "message" : "Success.",
    "status"  : 200,
    "content" : ""
}
```

or

```json
{
    "message" : "Bad request.",
        or
    "message" : "User with given ID is not present in the database.",
        or
    "message" : "Provided settings information is malformed.",
        or
    "message" : "The database server encountered an error, please try again.",

    "status"  : 500,
    "content" : ""
}
```