import os

# Base config
class Config(object):
    
    SERVER_URI = "0.0.0.0"
    DATABASE_NAME = os.environ["POSTGRES_DB"]
    SECRET_KEY = "Security is my passion. This is secure if you think about it i swear."
    SERVER_PORT = 5002

# Uses remote production server
class RemoteConfig(Config):
    SERVER_URI = "192.168.12.104"
    SERVER_PORT = 5000

class LocalConfig(Config):
    SERVER_URI = "0.0.0.0"

class TestingConfig(Config):
    TESTING = True
    SERVER_URI = "0.0.0.0"
    DATABASE_NAME = "testing"
    SECRET_KEY = "Super secret key"