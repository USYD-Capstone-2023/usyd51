#! /bin/bash

# Start test database
sudo python3 ../backend/app.py testing &
echo $! > db_pid.txt

# Start scanning server
sudo python3 ../scanning/scan_interface.py local &
echo $! > scan_pid.txt

# Run Auth tests
python3 -m unittest ./auth_tests.py

# Kill flask servers 
kill $(cat db_pid.txt)
kill $(cat scan_pid.txt)

# Delete pid files
rm db_pid.txt
rm scan_pid.txt

