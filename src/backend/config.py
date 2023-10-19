import os

# Base config
class Config(object):
    
    SERVER_URI = "127.0.0.1"
    POSTGRES_HOST = "localhost"
    SERVER_PORT = 5002
    POSTGRES_PORT = 5432
    POSTGRES_DB = "networks"
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = "root"
    SECRET_KEY = "Security is my passion. This is secure if you think about it i swear."


class DockerLocalConfig(Config):
    SERVER_URI = "0.0.0.0"
    SERVER_PORT = 5002
    POSTGRES_HOST = os.environ["POSTGRES_HOST"]
    POSTGRES_PORT = os.environ["POSTGRES_PORT"]
    POSTGRES_DB = os.environ["POSTGRES_DB"]
    POSTGRES_USER = os.environ["POSTGRES_USER"]
    POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
    SECRET_KEY = "Security is my passion. This is secure if you think about it i swear."

# Uses remote production server
class RemoteConfig(Config):
    SERVER_URI = "192.168.12.104"
    SERVER_PORT = 5000

class LocalConfig(Config):
    SERVER_URI = "0.0.0.0"

class TestingConfig(Config):
    TESTING = True
    SERVER_URI = "0.0.0.0"
    POSTGRES_DB = "testing"
    SECRET_KEY = "Super secret key"