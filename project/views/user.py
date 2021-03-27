from flask import Blueprint, render_template

user_blue = Blueprint("user", __name__, url_prefix="/u")


@user_blue.route("/")  # http://localhost/u
def user_home():
    return "User Home"


@user_blue.route("/help")
def user_help():
    return render_template("help.html", type="user")
