import datetime

from flask import Blueprint, render_template, request, jsonify, session, redirect

from ..database import *
from ..models import *

user_blue = Blueprint("user", __name__)


@user_blue.route("/board/create")
def create_post():
    Bid = request.args.get("Bid")
    if not Bid or not Bid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 404
    Uid = session.get("Uid")
    data = {"Bid": Bid}
    if not Uid:
        return redirect("/login")
    # check whether user is banned
    match_user: User = my_db.query(User, User.Uid == Uid, first=True)
    if match_user.banned:
        if match_user.banDuration > datetime.datetime.now():
            return jsonify({"error": {"msg": "user banned"}}), 404

    match_board = my_db.query(Board, Board.Bid == Bid)
    if not match_board:
        return jsonify({"error": {"msg": "invalid board ID"}}), 404
    return render_template("create.html", data=data)


@user_blue.route("/report")
def report():
    Uid = session.get("Uid")
    if not Uid:
        return redirect("/login")

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


@user_blue.route("/profile/<int:Uid>")
def get_personal_profile(Uid):
    u = my_db.query(User, User.Uid == Uid)
    if len(u) == 0:
        return "Not Found", 404
    user_info = {
        "nickname": u.nickname, "avatar": u.avatar, "timestamp": u.timestamp, "gender": u.gender,
        "phoneNumber": u.phoneNumber, "email": u.email, "address": u.address, "dateOfBirth": u.dateOfBirth,
        "banned": u.banned, "banDuration": u.banDuration
    }
    return render_template("profile.html", data=user_info)
