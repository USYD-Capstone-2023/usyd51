import sys
import subprocess

requirements = ["flask", "scapy", "python-nmap", "netifaces", "requests"]

for req in requirements:
    subprocess.check_call([sys.executable, "-m", "pip", "install", req])
