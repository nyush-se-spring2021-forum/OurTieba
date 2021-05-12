import time

from flask import Blueprint, jsonify, render_template, request

from ..configs.functions import *
from ..database import *
from ..models import *

user_blue = Blueprint("user", __name__)


@user_blue.route("/board/create")
@login_required
def create_post():
    """
    not used
    :return:
    """
    Uid = session["Uid"]

    # check whether user is banned
    match_user: User = my_db.query(User, User.Uid == Uid, first=True)
    if match_user.banned:
        if match_user.banDuration > datetime.datetime.utcnow():
            return jsonify({"error": {"msg": "user banned"}}), 404
    Bid = request.args.get("Bid")
    if not Bid or not Bid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 404

    match_board = my_db.query(Board, Board.Bid == Bid)
    if not match_board:
        return jsonify({"error": {"msg": "invalid board ID"}}), 404
    data = {"Bid": Bid}
    return render_template("login.html", data=data)


@user_blue.route("/report")
@login_required
def report():
    """
    This function is used to redirect the users to the report page
    :return: report.html
    """
    target = request.args.get("target", 0)
    id = request.args.get("id")
    data = {"id": id, "target": target}
    if target == "comment":
        match_result = my_db.query(Comment, Comment.Cid == id, first=True)
        if not match_result:
            return "Not Found", 404
        return render_template("report.html", data=data)
    elif target == "post":
        match_result = my_db.query(Post, Post.Pid == id, first=True)
        if not match_result:
            return "Not Found", 404
        return render_template("report.html", data=data)
    else:
        return "Invalid URL", 404


@user_blue.route("/notifications")
@login_required
def check_notification():
    Uid = session["Uid"]
    last_check = session["last_check"]

    cur_ts = time.time()
    match_ntf = my_db.query(Notification, and_(Notification.receiver == "user", Notification.Rid == Uid,
                                               Notification.timestamp.between(last_check, cur_ts)))
    ntfs = []
    for n in match_ntf:
        n: Notification
        ntfs.append({"starter": n.starter, "Sid": n.Sid, "target": n.target, "Tid": n.Tid,
                     "action": n.action, "timestamp": n.timestamp})
    data = {"ntfs": ntfs}
    my_db.update(User, User.Uid == Uid, values={"lastCheck": cur_ts})
    session["last_check"] = cur_ts
    return render_template("notifications.html", data=data)