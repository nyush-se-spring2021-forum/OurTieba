from flask import Blueprint, render_template

user = Blueprint("user", __name__, url_prefix="/u")


@user.route("/")  # http://localhost/u
def user_home():
    return "User Home"


@user.route("/help")
def user_help():
    return render_template("help.html", type="user")
