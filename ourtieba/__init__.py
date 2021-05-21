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


def create_app():
    app = Flask(__name__, static_url_path="/")
    config_app(app, env="development")

    with app.app_context():
        Moment(app)
        init_db(db_path=app.config['DATABASE_PATH'])
        enable_parser(app)
        register_route(app)
        register_blue(app)
        # init_logger(env="development")
        # init_scheduler(app)
    return app


def register_route(app):
    @app.teardown_appcontext
    def teardown_session(e):
        my_db.close()
        OT_spider.close()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("error/404.html"), 404

    @app.errorhandler(403)
    def access_forbidden(e):
        return render_template("error/403.html"), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("error/500.html"), 500

    @app.before_request
    def filter_request():
        if request.method not in ALLOWED_METHODS:
            return "Method Not Allowed", 405
        ua = str(request.user_agent)
        if "Mozilla" not in ua or "Gecko" not in ua:
            return "No Scrappers!", 403

    @app.after_request
    def set_res_headers(response):
        response.headers["Server"] = "OurTieba"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "sameorigin"
        if app.config.get("ENABLE_CSP"):
            response.headers["Content-Security-Policy"] = "script-src " + " ".join(WHITELIST) + "; object-src 'self'"
        return response

    @app.route("/prepare_ueditor")
    def prepare_ueditor_iframe():
        return render_template("prepare_ueditor.html")

    @app.template_filter("index_format")
    def add_zeros(i, length):  # format index in photos.html
        """
        Pad zeros to i, and turn it into a string. The length is at least 2.
        :param i: int. Integer to pad.
        :param length: int. Base integer.
        :return: A padded string.

        For example,
        add_zeros(1, 2) -> "01";
        add_zeros(1, 12) -> "01";
        add_zeros(13, 101) -> "013".
        """
        return ("{:0>" + str(max(len(str(length)), 2)) + "d}").format(i)
