# API Spec #

## Map Network ##

Gets all information required to map the network, including device IP addresses, MAC addresses, each device's parent node, MAC vendor, hostname. 
Registers data in the database with the network's SSID as the default name

Usage: ```/map_network```

Return format:
```python
{
    device_mac : {

        "hostname" : device_hostname,
        "ip" : device_ip,
        "mac" : device_mac_address,
        "mac_vendor" : device_mac_vendor,
        "os_family" : os_family,
        "os_type" : os_type,
        "os_vendor" : os_vendor,
        "parent" : parent_nodes_ip
    }, ...
}

or

{"error" : "Failed to scan network, are you connected to the internet?"}

```
All values default to "unknown" if they haven't been found.

## Rename Network ##

Renames a network to the desired name.

Usage: ```/rename_network/<old name>,<new name>```

Return format:
```python
"success"
or
"error"

```

## Get Network No Update ##

Returns all network information required to map the network from the database, does not run new scans but can contain new information from passive scanning.

Usage: ```/network/<network_name>```

Return format:
```python
{
    device_mac : {

        "hostname" : device_hostname,
        "ip" : device_ip,
        "mac" : device_mac_address,
        "mac_vendor" : device_mac_vendor,
        "os_family" : os_family,
        "os_type" : os_type,
        "os_vendor" : os_vendor,
        "parent" : parent_nodes_ip
    }, ...

}

or

{
    "error" : "Current network is not registered in the database, run /map_network to add this network to the database."
}
```

## OS Scan ##

Uses TCP fingerprinting to determine the most likely operating system for each device on the network.
Data is saved to database, then all device info is returned.

Usage: ```/os_info/<network_name>```

Return format:
```python
    "scan complete."
```

## DHCP Server Info ##

Returns the information of the DHCP server for the current connection.

Usage: ```/dhcp_info```

Return format:
```python
{
    "domain" : router_hostname,
    "iface" : network_interface,
    "router" : router_ip,
    "subnet_mask" : subnet_mask
}
```

## Request Progress ##

Gets the current progress information of the backend loading bar, used to synchronise with a frontend loading bar. CURRENTLY ONLY WORKS IF ONE REQUEST IS ISSUED AT A TIME!

Usage: ```/request_progress```

Return format:
```python
{
    "flag" : is the loading bar in use?,
    "progress" : number of units completed,
    "total" : total number of units,
   "label" : loading bar text
}
```

## Delete Network ##

Deletes a network from the database based on the network's gateway's MAC address

Usage: ```/delete_network/<network_name>```

Return format:
```python
    "Successfully deleted network"
    or
    "Could not find entered network..."
```

## SSID ##

Gets the SSID of the current network.

Usage: ```/ssid```

Return format:
```python
    <ssid>
```

## Network Names ##

Gets the name, ssid, id and name of each network in the database.

Usage: ```/network_names```

Return format:
```python
{
    "gateway_mac" : gateway_mac,
    "id" : id,
    "name" : name,
    "ssid" : ssid,
}
```

