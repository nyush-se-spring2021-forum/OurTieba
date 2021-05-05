import hashlib
import json
import re

from flask import Blueprint, jsonify, request
from requests_html import HTML

from ..configs import *
from ..database import *
from ..models import *

api = Blueprint("api", __name__, url_prefix="/api")


@api.route('/post/add', methods=["POST"])
@login_required
def add_post():
    Uid = session["Uid"]
    # check whether user is banned
    match_user: User = my_db.query(User, User.Uid == Uid, first=True)
    if match_user.banned:
        if match_user.banDuration > datetime.datetime.utcnow():
            return jsonify({"error": {"msg": "user banned"}, "status": 0})

    Bid = request.form.get("Bid")
    title = request.form.get("title")
    if not Bid or not Bid.isnumeric() or not title:
        return jsonify({"error": {"msg": "invalid data"}, "status": 0})

    match_board = my_db.query(Board, Board.Bid == Bid, first=True)
    if not match_board:
        return jsonify({"error": {"msg": "invalid board ID"}, "status": 0})
    match_board.postCount += 1

    content = request.form.get("content", "<p></p>")
    text = request.form.get("text", "")

    photos = []
    try:
        html = HTML(html=content)
    except Exception as e:
        return jsonify({"error": {"msg": e}, "status": 0})

    for ele in html.find("img"):
        src = ele.attrs.get("src")
        if src and src.startswith("/cdn/"):  # src = "/cdn/-3578255560995509753.png"
            photos.append(src[5:])

    new_post = Post(Uid, int(Bid), title, content, photos, text)
    my_db.add(new_post)
    return jsonify({"status": 1})


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

    status = CommentStatus if target == "comment" else PostStatus
    status_cond = CommentStatus.Cid == target_id if target == "comment" else PostStatus.Pid == target_id
    match_status = my_db.query(status, and_(status.Uid == Uid, status_cond), first=True)
    if not match_status:
        match_target.likeCount += int(action)
    elif (action == "1" and match_status.liked == 1) or (action == "0" and match_status.liked == 0):
        pass  # duplicate request, do not perform anything
    else:
        match_target.likeCount += 1 if action == "1" else -1
        match_target.dislikeCount -= match_status.disliked
    new_status = status(Uid, int(target_id), int(action), 0)
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

    status = CommentStatus if target == "comment" else PostStatus
    status_cond = CommentStatus.Cid == target_id if target == "comment" else PostStatus.Pid == target_id
    match_status = my_db.query(status, and_(status.Uid == Uid, status_cond), first=True)
    if not match_status:
        match_target.dislikeCount += int(action)
    elif (action == "1" and match_status.disliked == 1) or (action == "0" and match_status.disliked == 0):
        pass  # duplicate request, do not perform anything
    else:
        match_target.dislikeCount += 1 if action == "1" else -1
        match_target.likeCount -= match_status.liked
    new_status = status(Uid, int(target_id), 0, int(action))
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

    reporter = my_db.query(User, User.Uid == Uid, first=True)
    reporter.reports.append(new_report)
    return redirect(f"/post/{Pid}")


@api.route('/comment/add', methods=["POST"])
@login_required
def add_comment():
    Uid = session["Uid"]
    # check whether user is banned
    match_user: User = my_db.query(User, User.Uid == Uid, first=True)
    if match_user.banned:
        if match_user.banDuration > datetime.datetime.utcnow():
            return jsonify({"error": {"msg": "user banned"}, "status": 0})

    Pid = request.form.get("Pid")
    content = request.form.get("content")
    if not Pid or not Pid.isnumeric() or not content:
        return jsonify({"error": {"msg": "invalid data"}, "status": 0})

    text = request.form.get("text", "")  # can be None because comment may only contain photo

    photos = []
    try:
        html = HTML(html=content)
    except Exception as e:
        return jsonify({"error": {"msg": e}, "status": 0})

    for ele in html.find("img"):
        src = ele.attrs.get("src")
        if src and src.startswith("/cdn/"):  # src = "/cdn/-3578255560995509753.png"
            photos.append(src[5:])

    match_post = my_db.query(Post, Post.Pid == Pid, first=True)
    if not match_post:
        return jsonify({"error": {"msg": "invalid post ID"}, "status": 0})
    match_post.commentCount += 1
    match_post.latestCommentTime = datetime.datetime.utcnow()

    new_comment = Comment(Uid, Pid, content, photos, text)
    my_db.add(new_comment)
    return jsonify({"status": 1})


@api.route('/post/delete', methods=["POST"])
@login_required
def delete_post():
    Uid = session['Uid']

    Pid = request.form.get("Pid")
    Bid = request.form.get("Bid")
    if not Pid or not Pid.isnumeric() or not Bid or not Bid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 403

    match_post = my_db.query(Post, and_(Post.Pid == Pid, Post.Uid == Uid), first=True)
    if not match_post or match_post.under.Bid != int(Bid):
        return jsonify({"error": {"msg": "invalid post ID or board ID or user"}}), 403
    match_post.under.postCount -= 1

    my_db.delete(Post, Post.Pid == Pid)
    # Then delete all corresponding data in other relating tables
    result = my_db.query(Comment, Comment.Pid == Pid)
    for i in result:
        my_db.delete(CommentStatus, CommentStatus.Cid == i.Cid)
    my_db.delete(Comment, Comment.Pid == Pid)
    my_db.delete(PostStatus, PostStatus.Pid == Pid)
    return redirect(f"/board/{Bid}")


@api.route('/comment/delete', methods=["POST"])
@login_required
def delete_comment():  # will not alter post lastCommentTime
    Uid = session['Uid']

    Cid = request.form.get("Cid")
    Pid = request.form.get("Pid")
    if not Cid or not Cid.isnumeric() or not Pid or not Pid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 403
    match_comment = my_db.query(Comment, and_(Comment.Cid == Cid, Comment.Uid == Uid), first=True)
    if not match_comment:
        return jsonify({"error": {"msg": "invalid ID or user"}}), 403

    match_post = my_db.query(Post, Post.Pid == Pid, first=True)
    if not match_post or match_comment not in match_post.comments:
        return jsonify({"error": {"msg": "invalid comment ID or post ID"}}), 403
    match_post.commentCount -= 1

    my_db.delete(Comment, Comment.Cid == Cid)
    # Then delete all corresponding data in other relating tables
    my_db.delete(CommentStatus, CommentStatus.Cid == Cid)
    return redirect(f"/post/{Pid}")


@api.route('/personal_info/add', methods=["POST"])
@login_required
def add_personal_info():
    Uid = session["Uid"]

    nickname = request.form.get("nickname")
    if not nickname:
        return jsonify({"error": {"msg": "invalid data"}}), 403
    # check gender
    gender = request.form.get("gender")
    if gender not in ["male", "female", "other"]:
        return jsonify({"error": {"msg": "invalid gender"}}), 403
    # check phone number
    phone_number = request.form.get("phone_number")
    phone_number = re.findall(r"^[+]*[(]?[0-9]{1,4}[)]?[-\s./0-9]*$", phone_number)
    if not phone_number:
        return jsonify({"error": {"msg": "invalid phone number"}}), 403
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
        date_of_birth = datetime.datetime.strptime(date_of_birth, "%Y-%m-%d")
    except Exception as e:
        return jsonify({"error": {"msg": f"invalid date of birth: {e}"}}), 403

    my_db.update(User, User.Uid == Uid, values={"nickname": nickname, "gender": gender, "phoneNumber": phone_number,
                                                "email": email, "address": address, "dateOfBirth": date_of_birth})
    match_user = my_db.query(User, User.Uid == Uid, first=True)
    session.pop("user_info")
    session["user_info"] = {"nickname": match_user.nickname, "avatar": match_user.avatar}
    return redirect(f"/profile/{Uid}")


@api.route('/auth/register', methods=["POST"])
def register_auth():
    Uid = session.get("Uid")
    if Uid:
        return redirect("/")  # if already logged in, redirect to homepage

    # check username
    username = request.form.get("uname")
    if not username:
        return jsonify({"error": {"msg": "Invalid data"}, "status": 0})
    # (non-existence)
    match_user = my_db.query(User, User.uname == username, first=True)
    if match_user:
        return jsonify({"error": {"msg": "user already exists"}, "status": 0})
    # (validity)
    username = re.findall(r"[\w_]+$", username)
    if not username:
        return jsonify({"error": {"msg": "Invalid username"}, "status": 0})
    else:
        username = username[0]
    if len(username) < 5 or len(username) > 20:
        return jsonify({"error": {"msg": "username must be of length 5 ~ 20"}, "status": 0})
    # check password
    password = request.form.get("password")
    if not password:
        return jsonify({"error": {"msg": "Invalid data"}, "status": 0})
    password = re.findall(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", password)
    if not password:
        return jsonify({"error": {"msg": "Invalid password"}, "status": 0})
    else:
        password = password[0]
    # check nickname
    nickname = request.form.get("nickname")
    if not nickname or len(nickname) > 20:
        return jsonify({"error": {"msg": "Invalid nickname"}, "status": 0})

    new_user = User(password, username, nickname=nickname)
    my_db.add(new_user)

    # login once finish registration
    new_user = my_db.query(User, User.uname == username, first=True)
    session["Uid"] = new_user.Uid
    session["user_info"] = {"nickname": new_user.nickname, "avatar": new_user.avatar}
    return jsonify({"status": 1})


@api.route('/auth/login', methods=["POST"])
def login_auth():
    Uid = session.get("Uid")
    if Uid:
        return redirect("/")  # if already logged in, redirect to homepage

    data = request.form.to_dict()
    username = data.get("uname")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": {"msg": "Invalid input."}, "status": 0})

    match_user: User = my_db.query(User, User.uname == username, first=True)
    if not match_user:
        return jsonify({"error": {"msg": "Username does not exist."}, "status": 0})
    if hashlib.sha3_512(password.encode()).hexdigest() != match_user.password:
        return jsonify({"error": {"msg": "Incorrect password."}, "status": 0})
    session["Uid"] = match_user.Uid
    user_info = {"nickname": match_user.nickname, "avatar": match_user.avatar}
    session["user_info"] = user_info
    # session.permanent = True
    return jsonify({"status": 1, "Uid": match_user.Uid})


@api.route('/auth/logout', methods=["POST", "GET"])
@login_required
def logout_auth():
    session.clear()
    return "<script>location.replace(document.referrer);</script>", 200


@api.route("/upload", methods=["POST"])
@login_required
def save_file():
    Uid = session["Uid"]

    file = request.files.get("file")
    # check if file
    if not file:
        return jsonify({"error": {"msg": "please upload a file"}})
    # check file type
    file_type = file.content_type
    if not file_type or not file_type.startswith("image"):
        return jsonify({"error": {"msg": "invalid file type"}})
    file_type = file_type.split("/")[1]
    # check file size
    if int(request.headers["Content-Length"]) > 3 * 1024 * 1024:
        return jsonify({"error": {"msg": "image too large"}})

    path = CDN_PATH
    if not os.path.exists(path):  # os is imported in config.py
        os.mkdir(path)

    src = str(hash(str(Uid) + str(datetime.datetime.utcnow()))) + "." + file_type
    filepath = path + src
    while os.path.exists(filepath):
        src = str(hash(str(Uid) + str(datetime.datetime.utcnow()))) + "." + file_type
        filepath = path + src
    file.save(filepath)

    match_user = my_db.query(User, User.Uid == Uid, first=True)
    avatar = match_user.avatar
    if avatar != "default_avatar.jpg":
        old_path = path + avatar
        if os.path.exists(old_path):
            os.remove(old_path)

    my_db.update(User, User.Uid == Uid, values={"avatar": src})
    session.pop("user_info")
    session["user_info"] = {"nickname": match_user.nickname, "avatar": src}
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
    match_board.subscribeCount += 1 if action == "1" else -1

    new_sub = Subscription(Uid, Bid, int(action))
    my_db.merge(new_sub)
    return jsonify({"status": 1})


@api.route("/auth/set_password")
@login_required
def set_password():
    Uid = session["Uid"]

    # check password
    password = request.form.get("password")
    if not password:
        return jsonify({"error": {"msg": "Invalid data"}, "status": 0})
    password = re.findall(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", password)
    if not password:
        return jsonify({"error": {"msg": "Invalid password"}, "status": 0})
    else:
        password = hashlib.sha3_512(password[0].encode()).hexdigest()

    my_db.update(User, User.Uid == Uid, values={"password": password})
    return jsonify({"status": 1})


@api.route("/view")
def get_info():
    Cid = request.args.get("Cid", "").split(",")  # should separate by comma, e.g. Cid=1,2,3
    Pid = request.args.get("Pid", "").split(",")
    Bid = request.args.get("Bid", "").split(",")
    base_info = {"time": datetime.datetime.utcnow(), "status": 1, "data": {"comments": [], "posts": [], "boards": []}}
    for c in Cid:
        target = my_db.query(Comment, Comment.Cid == c, first=True)
        if not target:
            continue
        base_info["data"]["comments"].append({"Cid": target.Cid, "Pid": target.Pid, "Uid": target.Uid,
                                              "content": target.content, "timestamp": target.timestamp,
                                              "like_count": target.likeCount, "dislike_count": target.dislikeCount})
    for p in Pid:
        target = my_db.query(Post, Post.Pid == p, first=True)
        if not target:
            continue
        base_info["data"]["posts"].append({"Pid": target.Pid, "Bid": target.Bid, "Uid": target.Uid,
                                           "title": target.title, "content": target.content,
                                           "timestamp": target.timestamp, "comment_count": target.commentCount,
                                           "like_count": target.likeCount, "dislike_count": target.dislikeCount,
                                           "view_count": target.viewCount,
                                           "latest_comment_time": target.latestCommentTime})
    for b in Bid:
        target = my_db.query(Board, Board.Bid == b, first=True)
        if not target:
            continue
        base_info["data"]["boards"].append({"Bid": target.Bid, "name": target.name, "hot": target.hot,
                                            "timestamp": target.timestamp, "post_count": target.postCount,
                                            "view_count": target.viewCount, "subscribe_count": target.subscribeCount})
    return jsonify(base_info)


@api.route("/img/add", methods=["GET", "POST"])
def upload_img():
    action = request.args.get("action")
    if action == "config":  # config the ueditor, user may not be logged-in
        with open("project/static/ueditor/config.json", "r") as f:
            content = f.read()
        result = json.loads(content)
    elif action == "uploadimage":
        if not session.get("Uid"):
            return jsonify({"error": {"msg": "not logged in"}, "status": 0})
        Uid = session["Uid"]

        file = request.files.get("upfile")
        file_type = file.content_type
        file_type = file_type.split("/")[1]

        path = CDN_PATH
        if not os.path.exists(path):  # os is imported in config.py
            os.mkdir(path)
        file_size = request.headers["content-length"]

        src = str(hash(str(Uid) + str(datetime.datetime.utcnow()))) + "." + file_type
        filepath = path + src
        while os.path.exists(filepath):
            src = str(hash(str(Uid) + str(datetime.datetime.utcnow()))) + "." + file_type
            filepath = path + src
        file.save(filepath)

        result = {
            "state": "SUCCESS",
            "url": "/" + filepath,
            "title": "",
            "original": ""
        }
    else:
        result = {"error": 1}
    return jsonify(result)
