# API Spec #

## Map Network ##

Gets all information required to map the network, including device IP addresses, MAC addresses, each device's parent node, MAC vendor, hostname.

Usage: ```/map_network```

Return format:
```python
{
    router_mac : {
        device_mac : {

            "hostname" : device_hostname,
            "ip" : device_ip,
            "mac" : device_mac_address,
            "mac_vendor" : device_mac_vendor,
            "os_family" : os_family,
            "os_type" : os_type,
            "os_vendor" : os_vendor,
            "parent" : parent_nodes_ip
        }

    }
}
```

All values default to "unknown" if they haven't been found.

## OS Scan ##

Uses TCP fingerprinting to determine the most likely operating system for each device on the network.

Usage: ```/os_info```

Currently returns nothing, just updates devices in the database.


## DHCP Server Info ##

Returns the information of the DHCP server.

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