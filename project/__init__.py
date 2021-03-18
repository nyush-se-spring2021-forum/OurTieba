from flask import Flask, render_template
from .views import *


def create_app():
    app = Flask(__name__, static_url_path="/")
    app.config.update({
        "DEBUG": True,
        "TEMPLATES_AUTO_RELOAD": True
    })
    register_blue(app)
    return app