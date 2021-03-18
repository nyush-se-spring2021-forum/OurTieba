from ..views.user import *
from ..views.guest import *


def register_blue(app):
    app.register_blueprint(user)
    app.register_blueprint(guest)