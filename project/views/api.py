import datetime

from flask import Blueprint, render_template, request, session, jsonify, redirect

from ..database import *
from ..models import *

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/post/add", methods=["POST"])
def create_post():
    Uid = session.get("Uid")
    if not Uid:
        return jsonify({"error": {"msg": "Not logged in!"}}), 403
    Bid = request.form.get("Bid")
    if not Bid or not Bid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 403
    data = {"Bid": Bid}
    match_board = db_session.query(Board).filter(Board.Bid == Bid).all()
    if not match_board:
        return jsonify({"error": {"msg": "invalid board ID"}}), 403
    title = request.form.get("title")
    content = request.form.get("content")
    new_post = Post(Uid, int(Bid), title, content)
    db_session.add(new_post)
    db_session.commit()
    return redirect("/board/" + Bid)


@api.route("/like", methods=["POST"])
def like():
    Uid = session.get("Uid")
    if not Uid:
        return jsonify({"error": {"msg": "Not logged in!"}}), 403
    target = request.form.get("target")
    target_id = request.form.get("id")
    action = request.form.get("like")
    if target not in ["comment", "post"] or not target_id or not target_id.isnumeric() or action not in ["0", "1"]:
        return jsonify({"error": {"msg": "invalid data"}}), 403

    query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
        Post, Post.Pid == target_id)
    match_target = db_session.query(query_from).filter(filter_cond).all()
    if not match_target:
        return jsonify({"error": {"msg": "invalid target ID"}}), 403

    now = datetime.datetime.now()  # current timestamp
    status = CommentStatus if target == "comment" else PostStatus
    new_status = status(Uid, int(target_id), 0, 0, now) if action == "0" else status(Uid, int(target_id), 1, 0, now)
    db_session.merge(new_status)
    db_session.commit()
    return jsonify({"success": 1}), 200


@api.route("/dislike", methods=["POST"])
def dislike():
    Uid = session.get("Uid")
    if not Uid:
        return jsonify({"error": {"msg": "Not logged in!"}}), 403
    target = request.form.get("target")
    target_id = request.form.get("id")
    action = request.form.get("like")
    if target not in ["comment", "post"] or not target_id or not target_id.isnumeric() or action not in ["0", "1"]:
        return jsonify({"error": {"msg": "invalid data"}}), 403

    query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
        Post, Post.Pid == target_id)
    match_target = db_session.query(query_from).filter(filter_cond).all()
    if not match_target:
        return jsonify({"error": {"msg": "invalid target ID"}}), 403

    now = datetime.datetime.now()  # current timestamp
    status = CommentStatus if target == "comment" else PostStatus
    new_status = status(Uid, int(target_id), 0, 0, now) if action == "0" else status(Uid, int(target_id), 0, 1, now)
    db_session.merge(new_status)
    db_session.commit()
    return jsonify({"success": 1}), 200


@api.route('/report/add')
def report():
    Uid = session.get("Uid")
    if not Uid:
        return jsonify({"error": {"msg": "Not logged in!"}}), 403
    target = request.form.get("target")
    target_id = request.form.get("id")
    reason = request.form.get("reason")
    if target not in ["comment", "post"] or not target_id or not target_id.isnumeric() or not reason:
        return jsonify({"error": {"msg": "invalid data"}}), 403

    query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
        Post, Post.Pid == target_id)
    match_target = db_session.query(query_from).filter(filter_cond).all()
    if not match_target:
        return jsonify({"error": {"msg": "invalid target ID"}}), 403

    Pid = match_target[0].Pid
    # insert into db
    new_report = Report(Uid, target, int(target_id), reason)
    db_session.add(new_report)
    return redirect("/post/" + str(Pid))