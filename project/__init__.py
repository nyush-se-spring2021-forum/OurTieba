from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from .configs import *
from .database import *
from .models import *
from .scrapper import *
from .views import *


def create_app():
    app = Flask(__name__, static_url_path="/")
    Bootstrap(app)
    Moment(app)
    config_app(app)
    with app.app_context():
        init_db()
    register_blue(app)
    # init_scheduler(app)
    return app
