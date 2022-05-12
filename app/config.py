import os

app_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "ASECRETKEY"
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "ASECRETKEY"
    MONGODB_SETTINGS = {
        "db": "music-theory",
        "host": "localhost",
        "port": 27017,
    }


class DevelopementConfig(BaseConfig):
    ENV = 'development'
    DEBUG = True


class TestingConfig(BaseConfig):
    ENV = 'testing'
    DEBUG = True


class ProductionConfig(BaseConfig):
    ENV = 'production'
    DEBUG = False
