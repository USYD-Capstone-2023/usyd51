# Client Meeting 8
14/09/2023 2:30pm - 2:55pm

# Agenda
- Client Deployment Feedback and Questions
- Team Split
- Other

### Client Deployment Feedback and Questions
- Overall great progress
	- Polish and pull everything together
- The way we built it is funky, but it works
- Backend is okay until it scans networks
	- Confused to why python is doing the scans
	- They should go to the frontend or a vpn pseudo network to do the scans
- Why do we need to use Node.js?
	- To run electron
	- also to do data handling??
- How does electron work?
	- It runs chromium locally
	- could go full web based without it though
- If I have IP 10.88.112.234 and subnet mask 255.255.248.0 how many IPs will it scan?
	- 2^10
	- linear iteration through the range.

### Team split
- Team split over front and back end
- Should speed up dev

### Other Suggestions
- make more endpoints
- do network/map/\<id\> instead of /network\_map/\<id\>
	- will make things cleaner in the backend
- vpn tunnel from backend to frontend, allowing us to "see" the frontend, could be a bit tough though.
	- backend would need to be broken up a lot
- just have backend serve data. python scans and only scans on http request, then dumps data.


