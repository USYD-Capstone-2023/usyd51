# Base config
class Config(object):
    
    SERVER_URI = "127.0.0.1"
    DATABASE_NAME = "networks"
    SECRET_KEY = "Security is my passion. This is secure if you think about it i swear."

# Uses remote production server
class RemoteConfig(Config):
    SERVER_URI = "192.168.12.104"

class LocalConfig(Config):
    SERVER_URI = "127.0.0.1"

class TestingConfig(Config):
    TESTING = True
    SERVER_URI = "127.0.0.1"
    DATABASE_NAME = "testing"
    SECRET_KEY = "Super secret key"