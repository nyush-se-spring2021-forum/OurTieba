from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from .configs import *  # import configurations
from .database import *  # import database session
from .models import *  # import all the models
from .scrapper import *  # import scrapper
from .views import *  # import all the view
from .logger import *  # import logger


def create_app():
    app = Flask(__name__, static_url_path="/")
    Bootstrap(app)
    Moment(app)
    config_app(app)
    with app.app_context():
        init_db()
    register_blue(app)
    # init_logger()
    # init_scheduler(app)
    return app
