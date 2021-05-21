from ..configs.config import *
from ..configs.functions import *
from ..configs.macros import *


def config_app(app, env="default"):
    """
    Configure Flask application by Config class based on environment.
    :param app: Flask app instance.
    :param env: string to specify running environment. Options in config.py.
    :return: None.
    """
    app.config.from_object(config[env])
