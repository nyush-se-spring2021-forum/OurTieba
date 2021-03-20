from ..views.guest import *
from ..views.user import *


def register_blue(app):
    app.register_blueprint(user)
    app.register_blueprint(guest)