from flask import Flask, jsonify, redirect, request

from .database import *
from .models import *
from .views import *

# Macros
PAGE_SIZE = 10


def create_app():
    app = Flask(__name__, static_url_path="/")
    app.config.update({
        "DEBUG": True,
        "TEMPLATES_AUTO_RELOAD": True
    })
    with app.app_context():
        init_db()
    register_blue(app)
    return app