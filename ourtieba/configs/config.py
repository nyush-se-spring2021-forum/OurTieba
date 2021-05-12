import datetime
import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'something you will never guess')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TEMPLATES_AUTO_RELOAD = True


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=15)  # default is 31 days


config = {
    'development': DevelopmentConfig,
    'testing': ProductionConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
