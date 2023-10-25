import sys
import subprocess

requirements = ["flask", "scapy", "python-nmap","python3-nmap", "netifaces", "requests", "pyjwt", "flask-cors","pycryptodome","uni-curses", "unittest"]

for req in requirements:
    subprocess.check_call([sys.executable, "-m", "pip", "install", req])
