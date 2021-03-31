from flask import Flask, abort
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from .configs import *  # import configurations
from .database import *  # import database session
from .logger import *  # import logger
from .models import *  # import all the models
from .scheduler import *  # import scheduler
from .scrapper import *  # import scrapper
from .views import *  # import all the view


def create_app():
    app = Flask(__name__, static_url_path="/")
    config_app(app)
    with app.app_context():
        Bootstrap(app)
        Moment(app)
        init_db()
        register_blue(app)
        # init_logger()
        # init_scheduler(app)
    return app
