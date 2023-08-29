# Client Meeting 5
28/08/2023 3:30pm-3:50pm

### VPN network demo
- sam could ssh into it, but password wouldnt work
	- fixed during meeting
- ssh in
- install things
- we can run both front and back end on it
	- we can also just run the backend on it and use frontend locally

### Testing
- how to test backend lmao
	- it will be tough
	- continue to hit the same known device
	- somehow build a fake network and test suite
	- don't actually ping real devices, just "respond" with information and test output

### Future
- move away from json
- get it in a database, cian wrote some starter code for us :)
- table join might need some tweaking

### Other Cian concerns
- if we track ips seperately - how to do IP history?
- iPhones generate new mac addresses every time you connect to the network
	- thanks apple
	- we're gonna need to do some logic magic to get that working
- our network topology is wrong (probably)
	- hasnt mapped through switches correctly
	- on cians network
	- layer 3 switches should show up as a hop in the network
	- a dumb switch probably won't - which is fine
	- we could infer that dumb switches exist (multiple devices connected to the same port)

### visualisation design
- cytoscape could be really useful for it
- will probably use it


