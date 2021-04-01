from flask import Blueprint, render_template, session, redirect

guest = Blueprint("guest", __name__)


@guest.route("/register")
def register_interface():
    if session.get("Uid"):
        return redirect("/")
    return render_template("register.html")


@guest.route("/login")
def login_interface():
    if session.get("Uid"):
        return redirect("/")
    return render_template("login.html")
