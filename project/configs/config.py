import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Macros
PAGE_SIZE = 10
RECOMMEND_NUM_BOARD = 10
RECOMMEND_NUM_NEWS = 3


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'something you will never guess'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TEMPLATES_AUTO_RELOAD = True


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing': ProductionConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
