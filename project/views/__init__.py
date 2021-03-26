from ..views.guest import *
from ..views.user import *
from ..views.api import *
from ..views.admin import *


def register_blue(app):
    app.register_blueprint(user)
    app.register_blueprint(guest)
    app.register_blueprint(api)
    app.register_blueprint(admin)