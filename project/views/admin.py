from flask import Blueprint, redirect, render_template

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/")
def admin_hello():
    return redirect("/admin/dashboard")


@admin.route("/dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")