# API Spec #
## MAC Address Vendor Resolution ##

Looks up the vendor of each provided MAC address using the table of Organizationally Unique Identifiers (OUI) provided by the IEEE.

Usage: ```/mac_vendor/mac_0,mac_1,...,mac_n```

Return format: 
```python
{
    MAC_0 : Vendor_0,
    MAC_1 : Vendor_1,
    ...,
    MAC_n : Vendor_n
}
```

## Ping Sweep ##

Returns a list of pairs of IPs and MACs corresponding to each active device on the current network.

Usage: ```/devices```

Return format: 
```python
{
    IP_0 : MAC_0,
    IP_1 : MAC_0,
    ...,
    IP_n : MAC_n
}
```

## OS Scan ##

Uses TCP fingerprinting to determine the most likely operating system for each provided device on the network.

Usage: ```/os_info/ip_0,ip_1,...,ip_n```

Return format:
```python
{
    IP_0 : {"os_type" : os_type, "os_vendor" : os_vendor, "os_family" : os_family}, 
    IP_1 : {"os_type" : os_type, "os_vendor" : os_vendor, "os_family" : os_family}, 
    ..., 
    IP_n : {"os_type" : os_type, "os_vendor" : os_vendor, "os_family" : os_family}
}
```


## Hostname ##

Retrieves the hostname of the device corresponding to each of the given IP addresses.

Usage: ```/hostname/IP_0,IP_1,...,IP_n```

Return format:
```python
{
    IP_0 : Hostname_0,
    IP_1 : Hostname_1,
    ...,
    IP_n : Hostname_n
}
```

## Traceroute ##

Returns the list of routers that a packet takes to get from the gateway to each of the queried IP addresses.

Usage: ```/traceroute/IP_0,IP_1,...,IP_n```

Return format: 
```python
{
    IP_0 : [route_ip_0, route_ip_1, ..., route_ip_m],
    IP_1 : [route_ip_0, route_ip_1, ..., route_ip_l],
    ...,
    IP_n : [route_ip_0, route_ip_1, ..., route_ip_k],
}
```

## DHCP Server Info ##

Returns the DHCP info from the server

Usage: ```/dhcp_info```

Return format:
```python
{
    "broadcast_address" : broadcast_address, 
    "lease_time" : lease_time,
    "message-type" : message_type, 
    "name_server" : name_server,
    "rebinding_time" : rebinding_time, 
    "renewal_time" : renewal_time,
    "router" : router_ip, 
    "server_id" : server_ip, 
    "subnet_mask" : subnet_mask,
    "vendor_specific" : vendor_specific_info
}
```

OR

```python
{
    "error" : "Recieved no response from dhcp server after x seconds..."
}
```