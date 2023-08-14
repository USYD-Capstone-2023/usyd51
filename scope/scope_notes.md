# Project Scope Statement
## Background

It is difficult to quickly understand an unfamiliar network with many devices (i.e. what are all the devices, how are they connected, how can they be accessed) so that the network can be troubleshooted, monitored, adjusted, etc. with a full knowledge of what's on it.
Other solutions exist but require hardware from specific brands and for all devices to be of the same brand (Ubiquiti Unifi, Fritz Mesh, Aruba Airwaves)

## Aim

The aim is to contribute to/begin development on an open source, vendor agnostic network mapping, monitoring, and management tool. It will be able to find basic information about all devices on the network, display it in a user friendly map topology UI, and record that data over time. The tool will have a simple setup process and be able to run on any user machine.

## Objectives (SMART)

- Develop web-based GUI for displaying network topology data (current and historical), navigable with mouse and keyboard visually displaying device information and layout in both map and list format
- Develop a data storage solution for keeping track of past data and recording new data, local only
- Develop a backend tool that scans the current LAN for all connected devices and as much information as possible to gain from each one, and stores it in the data system
- Create user documentation that details how to setup and use the software, as well as detailed information on any advanced features

## Success Criteria

At minimum, success for the client would be developing a working version with the network scanning/mapping tool. Success will be measured by communicating with the client throughout development (demos, presentation, questions, etc) and receiving feedback on the suitability of the tool as it is developed. This will be translated into our formal scope documentation including user stories and goals for each sprint. The completion of these stories/goals will be used to measure the success of the project.

## Deliverables

- Software package/final product
- User documentation
- Development documentation, including meeting minutes/notes, research documentation, sprint plans, etc.
- Progress log videos for each client meeting

## Scope

- Scan a network and find all online devices
- Gather and record information about each device over time
- Ability to customise monitoring frequency/what information is checked per device
- Automatically provide information about the network itself (configuration, etc)
- View current and past network/device status and information in a GUI. There should be a visual map layout and a list layout for easier reading with sorting/filtering capabilities

## Out Scope

- Manage/control/execute commands remotely on devices and/or groups of devices on the network

## Milestones

- Client approval of scope
- First UI prototype
- First prototype of network scanner/logger backend tool
- Integrate front end and back end
- Week 6 Project Demo Presentation

## Human Resources

We had contact with an engineer at CISCO who works on a similar product called Meraki. This provided valuable insight into the implementation level details of a project such as ours.
We will attempt to reach out to other companies that create similar products such as Ubiquiti, Fritz, Aruba and more to get further feedback and expert opinions.
Our facilitator also has experience working on a similar project, and has many helpful insights into the mechanics and potential implementation of the product.

## Other Resources

Other resources used for this project will mainly be those for learning, such as tutorials, written guides and articles on related topics.
We will also do extensive research into similar products such as Unify, AirWave, SolarWinds, Mesh and LogicMonitor.

## Reporting/Meeting Frequency

Client meetings will be twice weekly, Mondays at 3:30pm and Thursdays at 2:30pm.