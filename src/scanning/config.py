import os

# Base config
class Config(object):
    POSTGRES_URI = "127.0.0.1:5002"
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5001
    

class DockerLocalConfig(Config):

    valid = True
    for req in ["POSTGRES_URI", "SERVER_HOST", "SERVER_HOST"]:
        if req not in os.environ.keys():
            valid = False

    if valid:
        POSTGRES_URI = os.environ["POSTGRES_URI"]
        SERVER_HOST = os.environ["SERVER_HOST"]
        SERVER_PORT = os.environ["SERVER_PORT"]

# Uses remote production server
class RemoteConfig(Config):
    POSTGRES_URI = "192.168.12.104:5002"
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5001

class LocalConfig(Config):
    POSTGRES_URI = "127.0.0.1:5002"
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5001