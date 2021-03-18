from flask import Blueprint, render_template

guest = Blueprint("guest", __name__, url_prefix="/g")


@guest.route("/")
def user_home():
    return "Guest Home"


@guest.route("/help")
def user_help():
    return render_template("help.html", type="guest")