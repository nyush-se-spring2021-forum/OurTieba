from ..configs.config import config


def config_app(app, env="default"):
    app.config.from_object(config[env])