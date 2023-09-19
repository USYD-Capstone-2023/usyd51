# Client Meeting 9
18/09/2023 3:30pm - 3:50pm


# Codebase Goals

### Structure
- Frontend - on user
- Scan - user or elsewhere
- Flask & DB - Remote

### Communication

#### Client:
- Scan and server will constinently communicate
	- Network info
- Frontend and database will also communicate
	- frontend mostly just reading from database
	- but also renames and deletion
#### Team:
- Scan and Frontend to communicate for scan process and current SSID info.
	- Could do it without connecting scan and frontend
	- But it means the frontend must know where the scanner is

# Questions
- Do we want local scanning capabilities? - remote scanning seems a bit commercial
- We could do a headless daemon constantly scanning a network.
	- build whatever, can reintegrate to frontend later
- PostgreSQL - locally fine? or host a remote while we develop?
	- Set it up on Cian's Rasp. Pi
	- This should be the same as a remote postgresql server

# Goals
- Focus on the changing structure
- Next week we can do more feature implimentation things













