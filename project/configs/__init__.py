from ..configs.config import *
from ..configs.macros import *
from ..configs.functions import *


def config_app(app, env="default"):
    app.config.from_object(config[env])