from flask import Flask, render_template, jsonify
from .views import *
from .database import *
from .models import *


def create_app():
    app = Flask(__name__, static_url_path="/")
    app.config.update({
        "DEBUG": True,
        "TEMPLATES_AUTO_RELOAD": True
    })
    init_db()
    register_blue(app)
    return app