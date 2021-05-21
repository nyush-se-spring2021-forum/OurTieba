from flask import Flask
from flask_moment import Moment

from .configs import *  # import configurations
from .database import *  # import database session
from .html_parser import *  # import html parser
from .logger import *  # import logger
from .models import *  # import all the models
from .scheduler import *  # import scheduler
from .scrapper import *  # import scrapper
from .views import *  # import all the view


def create_app(env="production"):
    """
    Create a Flask app instance under a given environment.
    :param env: environment under which the app will be created. See options in config.py.
    :return: a Flask app instance.
    """
    app = Flask(__name__, static_url_path="/")
    config_app(app, env=env)

    with app.app_context():
        Moment(app)
        init_db(app)
        enable_parser(app)
        register_route(app)
        register_blue(app)
        init_logger(app)
        init_scheduler(app)
    return app


def register_route(app):
    """
    Register routes to app.
    :param app: Flask app instance
    :return: None.
    """
    @app.teardown_appcontext
    def teardown_session(e):
        """
        Exit the context of my_db and OT_spider when app's context is teared down.
        :param e: event.
        :return: None.
        """
        my_db.close()
        OT_spider.close()

    @app.errorhandler(404)
    def page_not_found(e):
        """
        Render assigned template when error code 404 occurs.
        :param e: error event.
        :return: error/404.html.
        """
        return render_template("error/404.html"), 404

    @app.errorhandler(403)
    def access_forbidden(e):
        """
        Render assigned template when error code 403 occurs.
        :param e: error event.
        :return: error/403.html.
        """
        return render_template("error/403.html"), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        """
        Render assigned template when error code 500 occurs.
        :param e: error event.
        :return: error/500.html.
        """
        return render_template("error/500.html"), 500

    @app.before_request
    def filter_request():
        """
        Intercept requests with disallowed methods and/or fake user agent.
        :return: None.
        """
        if request.method not in ALLOWED_METHODS:
            return "Method Not Allowed", 405
        ua = str(request.user_agent)
        if "Mozilla" not in ua or "Gecko" not in ua:
            return "No Scrappers!", 403

    @app.after_request
    def set_res_headers(response):
        """
        Set headers to all responses.
        :param response: flask.wrappers.Response object.
        :return: response to send back to client.
        """
        response.headers["Server"] = "OurTieba"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "sameorigin"
        if app.config.get("ENABLE_CSP"):
            response.headers["Content-Security-Policy"] = "script-src " + " ".join(WHITELIST) + "; object-src 'self'"
        return response

    @app.template_filter("index_format")
    def add_zeros(i, length):  # format index in photos.html
        """
        Pad zeros to i, and turn it into a string. The length is at least 2. Used in photos.html.
        :param i: int. Integer to pad.
        :param length: int. Base integer.
        :return: A padded string.

        For example,
        add_zeros(1, 2) -> "01";
        add_zeros(1, 12) -> "01";
        add_zeros(13, 101) -> "013".
        """
        return ("{:0>" + str(max(len(str(length)), 2)) + "d}").format(i)
