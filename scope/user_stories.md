# User Stories
## List of Names
- Register and scan a new network
- Monitor the connected network over time and record data
- View network layout in a visual topology map
- View list of connected devices
- Load and view a saved network
- Load saved data upon reconnecting to a known network
- View device connection history
- View full network connection history

## User Types
Before fully defining the user stories, let's define a few types of users that will use the product in different ways and/or for different purposes.

- Basic users: Users with low to moderate technical experience (to be more clear, people who are quite comfortable using a computer, but not experts or highly knowledgable about networking) who want to visualise their home and/or small business network. They do this to check if any unknown devices are connected, to help troubleshoot basic connectivity issues, or to learn/out of interest. They should not be required to input data such as IP ranges or understand networking protocols.
- Advanced users: Computer enthusiasts, students, experts who have high technical experience and want to improve it. They want a convenient tool to visualise their network(s), monitor changes over time (coming and going devices), and to learn by exploring different network structures. They should be able to override automatic functions and control the tool at a low level. They want insights into what the tool is doing and how.
- Professional users: For example IT personnel, they have similar or greater knowledge to the advanced users, but want to use the tool for more and larger networks, to aid in gaining a quick understanding of an unfamiliar network and to help troubleshoot, manage, upgrade, merge, etc. a network. They want repeated actions such as discovering new networks and monitoring to require limited input, be mostly automatic and run independently to save the user time. They should be able to view large amounts of network data in a digestable format.

## User Story Definitions
### Name: Register and scan a new network
- As any user, given that I have not used the tool before on a network, I want to register the network in the tool and scan it, so that I can visualise it. 
- As a basic user, I want the process to be intuitive and not require knowledge of networking concepts or jargon.
- As an advanced or professional user, I want to be able to customise the process to use or not use specific protocols, and configure how the protocols are used.

### Name: Monitor the connected network over time and record data
- As a basic or advanced user, I want to be able to monitor the status of devices over time, so that I can work out which devices come and go, which devices are static, and in general discover any patterns.

### Name: View network layout in a visual topology map
- As any user, I want to view a network layout in a visual topology map, so that I can understand the network layout more easily.
- I want to see data about each device, so that I can understand what device each node is.
- I want to see which nodes are connected to each other, so that I can understand the netwwork structue and how each device is connected to the whole.

### Name: View list of connected devices
- As an advanced or professional user, I want to view the list of devices on the network in a sortable and filterable list format as well as the map view, so that I can more easily search for devices with certain traits/properties in a large network.

### Name: Load and view a saved network
- As any user, I want to be able to load and view a network I have scanned before even if not connected to it, so that I can continue inspecting the recorded data or show it to someone else even while offline.

### Name: Load saved data upon reconnecting to a known network
- As any user, I want the tool to automatically recognise that I am connected to a network I have scanned before, and allow me to load that network's saved data, so that I can easily keep all historical data for one network in one saved profile, and so that I don't have to set up the same network again.

### Name: View device connection history
- As a basic or advanced user, I want to view the connection history of individual devices, so that I can see patterns in their connectivity, monitor and troubleshoot connectivity issues with that device, and see if that device has been possibly been connected to any other network(s) I have scanned/monitored.
- As a professional user, I want to view the connection history of individual devices, so that I can better understand the usage and type of that device.

### Name: View full network connection history
- As any user, I want to view the connection history of all devices on the network at once, so that I can see trends in connectivity across the whole network.