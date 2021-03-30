import datetime
import hashlib
import re

from flask import Blueprint, request, session, jsonify, redirect

from ..database import *
from ..models import *

api = Blueprint("api", __name__, url_prefix="/api")


@api.route('/post/add', methods=["POST"])
def add_post():
    Uid = session.get("Uid")
    if not Uid:
        return redirect("/login")
    Bid = request.form.get("Bid")
    if not Bid or not Bid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 403

    match_board = my_db.query(Board, Board.Bid == Bid, first=True)
    #match_board = db_session.query(Board).filter(Board.Bid == Bid).first()
    if not match_board:
        return jsonify({"error": {"msg": "invalid board ID"}}), 403
    match_board.postCount += 1
    title = request.form.get("title")
    content = request.form.get("content")
    new_post = Post(Uid, int(Bid), title, content)
    my_db.add(new_post)
    return redirect(f"/board/{Bid}")


@api.route('/like', methods=["POST"])
def like():
    Uid = session.get("Uid")
    if not Uid:
        return redirect("/login")
    target = request.form.get("target")
    target_id = request.form.get("id")
    action = request.form.get("like")
    if target not in ["comment", "post"] or not target_id or not target_id.isnumeric() or action not in ["0", "1"]:
        return jsonify({"error": {"msg": "invalid data"}}), 403

    query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
        Post, Post.Pid == target_id)
    match_target = my_db.query(query_from, filter_cond, first=True)
    #match_target = db_session.query(query_from).filter(filter_cond).first()
    if not match_target:
        return jsonify({"error": {"msg": "invalid target ID"}}), 403
    match_target.likeCount += 1 if action == "1" else -1

    now = datetime.datetime.now()  # current timestamp
    status = CommentStatus if target == "comment" else PostStatus
    new_status = status(Uid, int(target_id), 1, 0, now) if action == "1" else status(Uid, int(target_id), 0, 0, now)
    my_db.merge(new_status)
    return jsonify({"success": 1}), 200


@api.route('/dislike', methods=["POST"])
def dislike():
    Uid = session.get("Uid")
    if not Uid:
        return redirect("/login")
    target = request.form.get("target")
    target_id = request.form.get("id")
    action = request.form.get("like")
    if target not in ["comment", "post"] or not target_id or not target_id.isnumeric() or action not in ["0", "1"]:
        return jsonify({"error": {"msg": "invalid data"}}), 403

    query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
        Post, Post.Pid == target_id)
    match_target = my_db.query(query_from, filter_cond, first=True)
    #match_target = db_session.query(query_from).filter(filter_cond).first()
    if not match_target:
        return jsonify({"error": {"msg": "invalid target ID"}}), 403
    match_target.dislikeCount += 1 if action == "1" else -1

    now = datetime.datetime.now()  # current timestamp
    status = CommentStatus if target == "comment" else PostStatus
    new_status = status(Uid, int(target_id), 0, 1, now) if action == "1" else status(Uid, int(target_id), 0, 0, now)
    my_db.merge(new_status)
    return jsonify({"success": 1}), 200


@api.route('/report/add', methods=["POST"])
def add_report():
    Uid = session.get("Uid")
    if not Uid:
        return redirect("/login")
    target = request.form.get("target")
    target_id = request.form.get("id")
    reason = request.form.get("reason")
    if target not in ["comment", "post"] or not target_id or not target_id.isnumeric() or not reason:
        return jsonify({"error": {"msg": "invalid data"}}), 403

    query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
        Post, Post.Pid == target_id)
    match_target = my_db.query(query_from, filter_cond, first=True)
    #match_target = db_session.query(query_from).filter(filter_cond).first()
    if not match_target:
        return jsonify({"error": {"msg": "invalid target ID"}}), 403

    Pid = match_target.Pid
    # insert into db
    new_report = Report(Uid, target, int(target_id), reason)
    my_db.add(new_report)
    return redirect(f"/post/{Pid}")


@api.route('/comment/add', methods=["POST"])
def add_comment():
    Uid = session.get("Uid")
    if not Uid:
        return redirect("/login")
    Pid = request.form.get("Pid")
    content = request.form.get("content")
    if not Pid or not Pid.isnumeric() or not content:
        return jsonify({"error": {"msg": "invalid data"}}), 403

    match_post = my_db.query(Post, Post.Pid == Pid, first=True)
    #match_post = db_session.query(Post).filter(Post.Pid == Pid).first()
    if not match_post:
        return jsonify({"error": {"msg": "invalid post ID"}}), 403
    match_post.commentCount += 1

    new_comment = Comment(Uid, Pid, content)
    my_db.add(new_comment)
    return redirect(f"/post/{Pid}?order=newest")


@api.route('/post/delete', methods=["POST"])
def delete_post():
    Uid = session.get("Uid")
    if not Uid:
        return redirect("/login")
    Pid = request.form.get("Pid")
    Bid = request.form.get("Bid")
    if not Pid or not Pid.isnumeric() or not Bid or not Bid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 403

    match_post = my_db.query(Post, Post.Pid == Pid, first=True)
    #match_post = db_session.query(Post).filter(Post.Pid == Pid).first()
    if not match_post or match_post.under.Bid != int(Bid):
        return jsonify({"error": {"msg": "invalid post ID or board ID"}}), 403
    match_post.under.postCount -= 1

    my_db.delete(Post, Post.Pid == Pid)
    #db_session.query(Post).filter(Post.Pid == Pid).delete()
    return redirect(f"/board/{Bid}")


@api.route('/comment/delete', methods=["POST"])
def delete_comment():
    Uid = session.get("Uid")
    if not Uid:
        return redirect("/login")
    Cid = request.form.get("Pid")
    Pid = request.form.get("Bid")
    if not Cid or not Cid.isnumeric() or not Pid or not Pid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 403

    match_post = my_db.query(Comment, Comment.Cid == Cid, first=True)
    #match_post = db_session.query(Comment).filter(Comment.Cid == Cid).first()
    if not match_post or match_post.comment_in.Pid != int(Pid):
        return jsonify({"error": {"msg": "invalid comment ID or post ID"}}), 403
    match_post.commentCount -= 1

    my_db.delete(Comment, Comment.Cid == Cid)
    #db_session.query(Comment).filter(Comment.Cid == Cid).delete()
    return redirect(f"/post/{Pid}")


@api.route('/personal_info/add', methods=["POST"])
def add_personal_info():
    Uid = session.get("Uid")
    if not Uid:
        return redirect("/login")

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

    personal_information = my_db.query(User, User.Uid == Uid, first=True)
    personal_information.gender = gender
    personal_information.phoneNumber = phone_number
    personal_information.email = email
    personal_information.address = address
    personal_information.dateOfBirth = date_of_birth
    #db_session.query(User).filter(User.Uid == Uid).update({"gender": gender, "phoneNumber": phone_number,
                                                           #"email": email, "address": address,
                                                           #"dateOfBirth": date_of_birth})
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
    #new_Uid = db_session.query(User).filter(User.uname == username).first().Uid
    session["Uid"] = new_Uid
    return redirect("/")


@api.route('/auth/login', methods=["POST"])
def login_auth():
    Uid = session.get("Uid")
    if Uid:
        return redirect("/")  # if already logged in, redirect to homepage

    username = request.form.get("uname")
    password = request.form.get("password")
    match_user = my_db.query(User, User.uname == username, first=True)
    #match_user = db_session.query(User).filter(User.uname == username).first()
    if not match_user:
        return jsonify({"error": {"msg": "user does not exist"}}), 403
    if hashlib.sha3_512(password.encode()).hexdigest() != match_user.password:
        return jsonify({"error": {"msg": "incorrect password"}}), 403
    session["Uid"] = match_user.Uid
    return redirect("/")


@api.route('/auth/logout', methods=["POST"])
def logout_auth():
    Uid = session.get("Uid")
    if not Uid:
        return redirect("/login")

    session.pop("Uid")
    return redirect("/")


@api.route("/upload", methods=["POST"])
def save_file():
    Uid = session.get("Uid")
    if not Uid:
        return redirect("/login")

    file = request.files["file"]
    src = str(hash(Uid + str(datetime.datetime.now()))) + ".png"

    """Not finished! Haven't checked whether file is legitimate."""
    with open(f"../../cdn/" + src, "wb") as f:
        f.write(file.read())
    my_db.query(User, User.Uid == Uid, first=True).avatar = src
    #db_session.query(User).filter(User.Uid == Uid).first().avatar = src
    return jsonify({"success": 1}), 200