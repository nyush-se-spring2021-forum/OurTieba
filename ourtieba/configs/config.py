import datetime
import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'something you will never guess')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TEMPLATES_AUTO_RELOAD = True
    ENABLE_CSP = False  # XSS protection: CSP header
    ENABLE_PARSER = True  # XSS protection: html parser


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    DATABASE_PATH = "sqlite:///test.db"
    LOGGER_PATH = "ourtieba/logs/test.log"


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False
    DATABASE_PATH = "sqlite:///OurTieba.db"
    LOGGER_PATH = "ourtieba/logs/OurTieba.log"

    ENABLE_CSP = True
    ENABLE_PARSER = False
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=15)  # default is 31 days


config = {
    'development': DevelopmentConfig,
    'testing': ProductionConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
