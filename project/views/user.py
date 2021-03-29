from flask import Blueprint, render_template, request, jsonify, session

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
        return render_template("create.html", data=data, error="Not logged in!")
    match_board = db_session.query(Board).filter(Board.Bid == Bid).all()
    if not match_board:
        return jsonify({"error": {"msg": "invalid board ID"}}), 404
    db_session.commit()
    return render_template("create.html", data=data)


@user_blue.route("/report")
def report():
    target = request.args.get("target", 0)
    id = request.args.get("id")
    data = {"id": id, "target": target}
    if target == "comment":
        match_result = db_session.query(Comment).filter(Comment.Cid == id).first()
        if not match_result:
            return "Not Found", 404
        db_session.commit()
        return render_template("report.html", data=data)
    elif target == "post":
        match_result = db_session.query(Post).filter(Post.Pid == id).first()
        if not match_result:
            return "Not Found", 404
        db_session.commit()
        return render_template("report.html", data=data)
    else:
        return "Invalid URL", 404


@user_blue.route("/profile/<int:Uid>")
def get_personal_profile(Uid):
    u = db_session.query(User).filter(User.Uid == Uid).all()
    if len(u) == 0:
        return "Not Found", 404
    user_info = {
        "nickname": u.nickname, "avatar": u.avatar, "timestamp": u.timestamp, "gender": u.gender,
        "phoneNumber": u.phoneNumber, "email": u.email, "address": u.address, "dateOfBirth": u.dateOfBirth,
        "banned": u.banned, "banDuration": u.banDuration
    }
    db_session.commit()
    return render_template("profile.html", data=user_info)
