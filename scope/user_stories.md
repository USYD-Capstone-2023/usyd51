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

- Basic users: Users with low to moderate technical experience (to be more clear, people who are quite comfortable using a computer, but not experts or highly knowledgeable about networking) who want to visualise their home and/or small business network. They do this to check if any unknown devices are connected, to help troubleshoot basic connectivity issues, or to learn/out of interest. They should not be required to input data such as IP ranges or understand networking protocols.
- Advanced users: Computer enthusiasts, students, experts who have high technical experience and want to improve it. They want a convenient tool to visualise their network(s), monitor changes over time (coming and going devices), and to learn by exploring different network structures. They should be able to override automatic functions and control the tool at a low level. They want insights into what the tool is doing and how.
- Professional users: For example IT personnel, they have similar or greater knowledge to the advanced users, but want to use the tool for more and larger networks, to aid in gaining a quick understanding of an unfamiliar network and to help troubleshoot, manage, upgrade, merge, etc. a network. They want repeated actions such as discovering new networks and monitoring to require limited input, be mostly automatic and run independently to save the user time. They should be able to view large amounts of network data in a digestible format.

## User Story Definitions
### Name: Register and scan a new network
- As any user, given that I have not used the tool before on a network, I want to register the network in the tool and scan it, so that I can visualise it. 
- As a basic user, I want the process to be intuitive and not require knowledge of networking concepts or jargon.
- As an advanced or professional user, I want to be able to customise the process to use or not use specific protocols, and configure how the protocols are used.

##### Acceptance criteria:
- When opening the tool, the user should be provided with a clear and intuitive option to register a new network.
- The tool should provide feedback on the progress of the network scan.
	- The basic user should be able to register and scan a network without encountering technical networking language which they may not understand.		
	- The advanced user should be able to register and scan a network and have constant feedback of technical details/activities of the program (inverse to the previous criteria).
- Upon completing the scan, the tool should confirm the successful registration and scanning of the network and display the network.

### Name: Monitor the connected network over time and record data
- As a basic or advanced user, I want to be able to monitor the status of devices over time, so that I can work out which devices come and go, which devices are static, and in general discover any patterns.

##### Acceptance criteria:
- Users should be able to manually trigger a network status update.
- Users should be able to schedule a rescan of the network at specific time intervals. These intervals should be separate for disconnect scans and new device scans.
- Maintain a log file of when devices join or leave a network, with an option of seeing this information neatly displayed within the app.

### Name: View network layout in a visual topology map
- As any user, I want to view a network layout in a visual topology map, so that I can understand the network layout more easily.
- I want to see data about each device, so that I can understand what device each node is.
- I want to see which nodes are connected to each other, so that I can understand the network structure and how each device is connected to the whole.

##### Acceptance criteria:
- Upon selecting an existing network or after the creation of an new one, users should see a graphical representation of the network.
- Each device node should be clickable to display more information about the device.
- Nodes should clearly indicate connections to other nodes.
- The network view should be zoomable and draggable for better visualization.
- Different types of devices or connections should have distinct visual representations.

### Name: View list of connected devices
- As an advanced or professional user, I want to view the list of devices on the network in a sortable and filterable list format as well as the map view, so that I can more easily search for devices with certain traits/properties in a large network.

##### Acceptance criteria:
- An option should be provided to view the network in list format. The list should allow for sorting by device properties like mac, type, or last connected time.
- This list of connected device should also be connected to viewing the devices history
- The list should update when devices are discovered/lost

### Name: Load and view a saved network
- As any user, I want to be able to load and view a network I have scanned before even if not connected to it, so that I can continue inspecting the recorded data or show it to someone else even while offline.

##### Acceptance criteria:
- Users should have a clear option to load previously scanned networks.
- Loaded networks should display all previously recorded data and configurations.
- When loading the network, give the user the option to check for just disconnected devices or for both disconnected and new devices.
- Create a preference which allows users to always do the same option when opening specific networks i.e remember to always only check for disconnected devices.

### Name: Load saved data upon reconnecting to a known network
- As any user, I want the tool to automatically recognise that I am connected to a network I have scanned before, and allow me to load that network's saved data, so that I can easily keep all historical data for one network in one saved profile, and so that I don't have to set up the same network again.

##### Acceptance criteria:
- The app should auto-detect previously scanned networks upon connection and ask if we'd like to load this network.

### Name: View device connection history
- As a basic or advanced user, I want to view the connection history of individual devices, so that I can see patterns in their connectivity, monitor and troubleshoot connectivity issues with that device, and see if that device has been possibly been connected to any other network(s) I have scanned/monitored.
- As a professional user, I want to view the connection history of individual devices, so that I can better understand the usage and type of that device.

##### Acceptance criteria:
- Users should be able to select any device and view its connection history.
- Connection history should display dates, times, and durations of connectivity.

### Name: View full network connection history
- As any user, I want to view the connection history of all devices on the network at once, so that I can see trends in connectivity across the whole network.

##### Acceptance criteria:
- A comprehensive connection history section should display connectivity data for the entire network. This should include infomation such as total uptime of all devices, number of unreachable devices due to connection issues, etc.
- Allows sorting the device status by several filters such as time of latest or oldest connect, single mac or ip, neighbouring devices and routing path of individual devices.
- Devices with several connects & disconnects or other abnormal activity should be flagged.