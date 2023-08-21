# Conversation Transcript
### I have removed the developers name for security reasons

### Ethan:
Hi [DEVELOPER]

I Hope you've been well!

I have just been given my end of degree client project with my university and It is to build an application that can determine the 
brand-agnostic topology of a network (very similar to the meraki topology view). I was wondering if i might be able to ask if you 
know how the information for the meraki topology view is gathered? is it something that each of the devices (switches etc.) tells 
the cloud? or is it like a custom ident protocol propogated through the network? I totally understand if you can't tell me much but 
any tips or feedback would be amazing! 🙂 

### [DEVELOPER]:
Hey man, sorry for late reply. The meraki topology, there’s is no much secret there it’s just using LLDP and CDP. If you haven’t 
looked into those protocols yet, you probably will have to deal with them soon 😁 they are basically the industry standard for 
network device discovery and things like you are trying to do.

The only difference with Meraki (and I think other vendors do this too) is that you have extra information because devices can 
recognise they are part of the same Meraki dashboard

One general problem about vendor-agnostic topologies and monitoring tools is that these network discovery protocols don’t provide 
much information

There are other things you query (eg syslog, SNMP, or even APIs) for more information but not all vendors define this the same way..
which is what makes it difficult too

If you haven’t already, you should research a bit more about SolarWinds… they were the ones that tried to build this kind of vendor 
agnostic network monitoring tool

### Ethan:
Awesome! this is some great information! I havent heard of SolarWinds before but ill be sure to take a look! We expected that default 
protocols wouldn't provide very much information but i will definitely have a look at the other things you mentioned. Thank you so 
much for taking the time to help me with this 🙂
