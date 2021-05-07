from flask import Blueprint, render_template, session, redirect

guest = Blueprint("guest", __name__)


@guest.route("/register")
def register_interface():
    """
    This function is used for the guests to register
    :return: register.html, which is the register page
    """
    if session.get("Uid"):
        return redirect("/")
    return render_template("register.html")


@guest.route("/login")
def login_interface():
    """
    This function is used for the guests to login
    :return: login.html, which is the login page
    """
    if session.get("Uid"):
        return redirect("/")
    return render_template("login.html")
