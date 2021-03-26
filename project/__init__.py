from flask import Flask, jsonify, redirect, request

from .database import *
from .models import *
from .views import *
from .scrapper import *

# Macros
PAGE_SIZE = 10
RECOMMEND_NUM_BOARD = 10
RECOMMEND_NUM_NEWS = 3


def create_app():
    app = Flask(__name__, static_url_path="/")
    app.config.update({
        "DEBUG": True,
        "TEMPLATES_AUTO_RELOAD": True
    })
    with app.app_context():
        init_db()
    register_blue(app)
    # init_scheduler(app)
    return app
