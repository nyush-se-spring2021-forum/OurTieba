import datetime
import hashlib
import re

from flask import Blueprint, request, jsonify, json

from ..database import *
from ..configs import *
from ..models import *

api = Blueprint("api", __name__, url_prefix="/api")


@api.route('/post/add', methods=["POST"])
@login_required
def add_post():
    Uid = session["Uid"]
    # check whether user is banned
    match_user: User = my_db.query(User, User.Uid == Uid, first=True)
    if match_user.banned:
        if match_user.banDuration > datetime.datetime.now():
            return jsonify({"error": {"msg": "user banned"}}), 404

    Bid = request.form.get("Bid")
    if not Bid or not Bid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 403

    match_board = my_db.query(Board, Board.Bid == Bid, first=True)
    if not match_board:
        return jsonify({"error": {"msg": "invalid board ID"}}), 403
    match_board.postCount += 1
    title = request.form.get("title")
    content = request.form.get("content")
    new_post = Post(Uid, int(Bid), title, content)
    my_db.add(new_post)
    return redirect(f"/board/{Bid}")


@api.route('/like', methods=["POST"])
@login_required
def like():
    Uid = session["Uid"]
    target = request.form.get("target")
    target_id = request.form.get("id")
    action = request.form.get("like")
    if target not in ["comment", "post"] or not target_id or not target_id.isnumeric() or action not in ["0", "1"]:
        return jsonify({"error": {"msg": "invalid data"}}), 403

    query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
        Post, Post.Pid == target_id)
    match_target = my_db.query(query_from, filter_cond, first=True)
    if not match_target:
        return jsonify({"error": {"msg": "invalid target ID"}}), 403
    match_target.likeCount += 1 if action == "1" else -1

    now = datetime.datetime.now()  # current timestamp
    status = CommentStatus if target == "comment" else PostStatus
    new_status = status(Uid, int(target_id), int(action), 0, now)
    my_db.merge(new_status)
    return jsonify({"success": 1}), 200


@api.route('/dislike', methods=["POST"])
@login_required
def dislike():
    Uid = session["Uid"]
    target = request.form.get("target")
    target_id = request.form.get("id")
    action = request.form.get("like")
    if target not in ["comment", "post"] or not target_id or not target_id.isnumeric() or action not in ["0", "1"]:
        return jsonify({"error": {"msg": "invalid data"}}), 403

    query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
        Post, Post.Pid == target_id)
    match_target = my_db.query(query_from, filter_cond, first=True)
    if not match_target:
        return jsonify({"error": {"msg": "invalid target ID"}}), 403
    match_target.dislikeCount += 1 if action == "1" else -1

    now = datetime.datetime.now()  # current timestamp
    status = CommentStatus if target == "comment" else PostStatus
    new_status = status(Uid, int(target_id), 0, int(action), now)
    my_db.merge(new_status)
    return jsonify({"success": 1}), 200


@api.route('/report/add', methods=["POST"])
@login_required
def add_report():
    Uid = session["Uid"]
    target = request.form.get("target")
    target_id = request.form.get("id")
    reason = request.form.get("reason")
    if target not in ["comment", "post"] or not target_id or not target_id.isnumeric() or not reason:
        return jsonify({"error": {"msg": "invalid data"}}), 403

    query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
        Post, Post.Pid == target_id)
    match_target = my_db.query(query_from, filter_cond, first=True)
    if not match_target:
        return jsonify({"error": {"msg": "invalid target ID"}}), 403

    Pid = match_target.Pid
    # insert into db
    new_report = Report(Uid, target, int(target_id), reason)
    my_db.add(new_report)

    reporter = my_db.query(User, User.Uid == Uid)
    reporter.reports.append(new_report)
    return redirect(f"/post/{Pid}")


@api.route('/comment/add', methods=["POST"])
@login_required
def add_comment():
    Uid = session["Uid"]
    # check whether user is banned
    match_user: User = my_db.query(User, User.Uid == Uid, first=True)
    if match_user.banned:
        if match_user.banDuration > datetime.datetime.now():
            return jsonify({"error": {"msg": "user banned"}}), 404

    Pid = request.form.get("Pid")
    content = request.form.get("content")
    if not Pid or not Pid.isnumeric() or not content:
        return jsonify({"error": {"msg": "invalid data"}}), 403

    match_post = my_db.query(Post, Post.Pid == Pid, first=True)
    if not match_post:
        return jsonify({"error": {"msg": "invalid post ID"}}), 403
    match_post.commentCount += 1
    match_post.lastCommentTime = datetime.datetime.now()

    new_comment = Comment(Uid, Pid, content)
    my_db.add(new_comment)
    return redirect(f"/post/{Pid}?order=newest")


@api.route('/post/delete', methods=["POST"])
@login_required
def delete_post():
    Pid = request.form.get("Pid")
    Bid = request.form.get("Bid")
    if not Pid or not Pid.isnumeric() or not Bid or not Bid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 403

    match_post = my_db.query(Post, Post.Pid == Pid, first=True)
    if not match_post or match_post.under.Bid != int(Bid):
        return jsonify({"error": {"msg": "invalid post ID or board ID"}}), 403
    match_post.under.postCount -= 1

    my_db.delete(Post, Post.Pid == Pid)
    return redirect(f"/board/{Bid}")


@api.route('/comment/delete', methods=["POST"])
@login_required
def delete_comment():  # will not alter post lastCommentTime
    Cid = request.form.get("Pid")
    Pid = request.form.get("Bid")
    if not Cid or not Cid.isnumeric() or not Pid or not Pid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 403

    match_post = my_db.query(Comment, Comment.Cid == Cid, first=True)
    if not match_post or match_post.comment_in.Pid != int(Pid):
        return jsonify({"error": {"msg": "invalid comment ID or post ID"}}), 403
    match_post.commentCount -= 1

    my_db.delete(Comment, Comment.Cid == Cid)
    return redirect(f"/post/{Pid}")


@api.route('/personal_info/add', methods=["POST"])
@login_required
def add_personal_info():
    Uid = session["Uid"]

    # check gender
    gender = request.form.get("gender")
    if gender not in ["male", "female", "other"]:
        return jsonify({"error": {"msg": "invalid gender"}}), 403
    # check phone number
    phone_number = request.form.get("phone_number")
    phone_number = re.findall(r"^[+]*[(]?[0-9]{1,4}[)]?[-\s./0-9]*$", phone_number)
    if not phone_number:
        return jsonify({"error": {"msg": "invalid gender"}}), 403
    else:
        phone_number = phone_number[0]
    # check email
    email = request.form.get("email")
    email = re.findall(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)
    if not email:
        return jsonify({"error": {"msg": "invalid email"}}), 403
    else:
        email = email[0]
    # check address
    address = request.form.get("address")
    if len(address) > 200:
        return jsonify({"error": {"msg": "invalid address"}}), 403
    # check date of birth
    date_of_birth = request.form.get("date_of_birth")
    try:
        date_of_birth = datetime.datetime.strptime(date_of_birth, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return jsonify({"error": {"msg": f"invalid date of birth: {e}"}}), 403

    match_user = my_db.query(User, User.Uid == Uid, first=True)
    match_user.gender = gender
    match_user.phoneNumber = phone_number
    match_user.email = email
    match_user.address = address
    match_user.dateOfBirth = date_of_birth
    return redirect(f"/profile/{Uid}")


@api.route('/auth/register', methods=["POST"])
def register_auth():
    Uid = session.get("Uid")
    if Uid:
        return redirect("/")  # if already logged in, redirect to homepage

    # check username
    username = request.form.get("uname")
    if len(username) < 5 or len(username) > 20:
        return jsonify({"error": {"msg": "invalid username"}}), 403
    username = re.findall(r"[\w_]+$", username)
    if not username:
        return jsonify({"error": {"msg": "invalid username"}}), 403
    else:
        username = username[0]
    # check password
    password = request.form.get("password")
    password = re.findall(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", password)
    if not password:
        return jsonify({"error": {"msg": "invalid password"}}), 403
    else:
        password = password[0]
    # check nickname
    nickname = request.form.get("nickname")
    if not nickname or len(nickname) > 20:
        return jsonify({"error": {"msg": "invalid nickname"}}), 403

    new_user = User(password, username, nickname=nickname)
    my_db.add(new_user)

    # login once finish registration
    new_Uid = my_db.query(User, User.uname == username, first=True).Uid
    session["Uid"] = new_Uid
    return redirect("/")


@api.route('/auth/login', methods=["POST"])
def login_auth():
    Uid = session.get("Uid")
    if Uid:
        return redirect("/")  # if already logged in, redirect to homepage

    data = request.form.to_dict()
    username = data.get("uname")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": {"msg": "invalid data"}, "status": 0})

    match_user = my_db.query(User, User.uname == username, first=True)
    if not match_user:
        return jsonify({"error": {"msg": "user does not exist"}, "status": 0})
    if hashlib.sha3_512(password.encode()).hexdigest() != match_user.password:
        return jsonify({"error": {"msg": "incorrect password"}, "status": 0})
    session["Uid"] = match_user.Uid
    return jsonify({"status": 1})


@api.route('/auth/logout', methods=["POST"])
@login_required
def logout_auth():
    session.pop("Uid")
    return redirect("/")


@api.route("/upload", methods=["POST"])
@login_required
def save_file():
    Uid = session["Uid"]

    file = request.files["file"]
    src = str(hash(Uid + str(datetime.datetime.now()))) + ".png"

    """Not finished! Haven't checked whether file is legitimate."""
    with open(f"../../cdn/" + src, "wb") as f:
        f.write(file.read())
    match_user = my_db.query(User, User.Uid == Uid, first=True)
    match_user.avatar = src
    return jsonify({"status": 1})


@api.route("/subscribe", methods=["POST"])
@login_required
def subscribe():
    Uid = session["Uid"]

    Bid = request.form.get("Bid")
    action = request.form.get("subscribe")  # "0"=unsub, "1"=sub
    if not Bid or not Bid.isnumeric() or action not in ["0", "1"]:
        return jsonify({"error": {"msg": "invalid data"}}), 403

    match_board = my_db.query(Board, Board.Bid == Bid, first=True)
    if not match_board:
        return jsonify({"error": {"msg": "invalid board ID"}}), 403

    new_sub = Subscription(Uid, Bid, int(action), datetime.datetime.now())
    my_db.merge(new_sub)
    return jsonify({"status": 1})