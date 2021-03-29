from flask import Blueprint, render_template

guest = Blueprint("guest", __name__)


@guest.route("/register")
def register_interface():
    return render_template("register.html")


@guest.route("/login")
def login_interface():
    return render_template("login.html")
