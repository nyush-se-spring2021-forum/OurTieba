from flask import Blueprint, render_template, request, abort

from ..configs.functions import *
from ..models import *

user_blue = Blueprint("user", __name__)


@user_blue.route("/report")
@login_required
def report():
    """
    This function is used to redirect the users to the report page
    :return: report.html
    """
    target = request.args.get("target")
    id = request.args.get("id")
    if not target or not id or not id.isnumeric() or target not in ("comment", "post"):
        abort(404)

    query_from = Comment if target == "comment" else Post
    if not query_from.exists(id):
        abort(404)

    data = {"id": id, "target": target}
    return render_template("report.html", data=data)


@user_blue.route("/notifications")
@login_required
def notification_interface():
    return render_template("notifications.html")
