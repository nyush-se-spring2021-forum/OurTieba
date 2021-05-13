import hashlib
import json
import re
import time

from flask import Blueprint, jsonify, request
from requests_html import HTML

from ..configs import *
from ..database import *
from ..models import *

api = Blueprint("api", __name__, url_prefix="/api")


@api.route('/post/add', methods=["POST"])
@login_required
def add_post():
    """
    This function is used for logged in users to create new post under a board
    :return: json information:
    if the creation is successful it will return status 1 otherwise it will return error message
    """
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

    if len(title) > 150:
        return jsonify({"error": {"msg": "Title word count exceeded. Maximum: 150"}, "status": 0})

    match_board = my_db.query(Board, Board.Bid == Bid, first=True)
    if not match_board:
        return jsonify({"error": {"msg": "invalid board ID"}, "status": 0})
    match_board.postCount += 1

    content = request.form.get("content", "<p></p>")
    text = request.form.get("text", "")
    if not content:  # unknown bug, the get above does not work
        content = "<p></p>"

    if len(text) > 2000:
        return jsonify({"error": {"msg": "Content word count exceeded. Maximum: 2000"}, "status": 0})

    try:
        html = HTML(html=content)
    except Exception as e:
        return jsonify({"error": {"msg": e}, "status": 0})

    medias = []
    for ele in html.find("img.OT_image,iframe.OT_video"):
        src = ele.attrs.get("src")
        if src:
            tag = ele.tag
            path = PHOTO_PATH if tag == "img" else VIDEO_PATH
            medias.append(path + src.split("/")[-1])

    new_post = Post(Uid, int(Bid), title, content, medias, text)
    my_db.add(new_post)
    return jsonify({"status": 1})


@api.route('/like', methods=["POST"])
@login_required
def like():
    """
    This function is used for logged in users to like a comment or post
    :return: json information:
    if the process is successful it will return status 1 otherwise it will return error message
    """
    Uid = session["Uid"]
    target = request.form.get("target")
    target_id = request.form.get("id")

    if target not in ("comment", "post") or not target_id or not target_id.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}, "status": 0})

    query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
        Post, Post.Pid == target_id)
    match_target = my_db.query(query_from, filter_cond, first=True)
    if not match_target:
        return jsonify({"error": {"msg": "invalid target ID"}, "status": 0})
    if match_target.status != 0:
        return jsonify({"error": {"msg": "Object not exists"}, "status": 0})

    status = CommentStatus if target == "comment" else PostStatus
    status_cond = CommentStatus.Cid == target_id if target == "comment" else PostStatus.Pid == target_id
    match_status = my_db.query(status, and_(status.Uid == Uid, status_cond), first=True)

    if not match_status:
        cur_status = 1
        new_status = status(Uid, int(target_id), cur_status, 0)
        my_db.add(new_status)
        match_target.likeCount += 1
    else:
        liked = match_status.liked
        disliked = match_status.disliked
        cur_status = 0 if liked else 1
        new_status = status(Uid, int(target_id), cur_status, 0, datetime.datetime.utcnow())
        my_db.merge(new_status)
        match_target.likeCount += -1 if liked else 1
        match_target.dislikeCount -= 1 if disliked else 0

    cur_target = my_db.query(query_from, filter_cond, first=True)
    cur_like, cur_dislike = cur_target.likeCount, cur_target.dislikeCount
    return jsonify({"cur_status": cur_status, "like_count": cur_like, "dislike_count": cur_dislike, "status": 1})


@api.route('/dislike', methods=["POST"])
@login_required
def dislike():
    """
    This function is used for logged in users to dislike a comment or post
    :return: json information:
    if the process is successful it will return status 1 otherwise it will return error message
    """
    Uid = session["Uid"]
    target = request.form.get("target")
    target_id = request.form.get("id")

    if target not in ("comment", "post") or not target_id or not target_id.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}, "status": 0})

    query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
        Post, Post.Pid == target_id)
    match_target = my_db.query(query_from, filter_cond, first=True)
    if not match_target:
        return jsonify({"error": {"msg": "invalid target ID"}, "status": 0})
    if match_target.status != 0:
        return jsonify({"error": {"msg": "Object not exists"}, "status": 0})

    status = CommentStatus if target == "comment" else PostStatus
    status_cond = CommentStatus.Cid == target_id if target == "comment" else PostStatus.Pid == target_id
    match_status = my_db.query(status, and_(status.Uid == Uid, status_cond), first=True)

    if not match_status:
        cur_status = 1
        new_status = status(Uid, int(target_id), 0, 1)
        my_db.add(new_status)
        match_target.dislikeCount += 1
    else:
        liked = match_status.liked
        disliked = match_status.disliked
        cur_status = 0 if disliked else 1
        new_status = status(Uid, int(target_id), 0, cur_status, datetime.datetime.utcnow())
        my_db.merge(new_status)
        match_target.dislikeCount += -1 if disliked else 1
        match_target.likeCount -= 1 if liked else 0

    cur_target = my_db.query(query_from, filter_cond, first=True)
    cur_like, cur_dislike = cur_target.likeCount, cur_target.dislikeCount
    return jsonify({"cur_status": cur_status, "like_count": cur_like, "dislike_count": cur_dislike, "status": 1})


@api.route('/report/add', methods=["POST"])
@login_required
def add_report():
    """
    This function is used for logged in users to report a post
    :return: if the report is successful, it will redirect the user to the previous post page
    otherwise, it will return json error message
    """
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
    """
    This function is used for logged in users to create new comment under a post
    :return: json information:
    if the creation is successful it will return status 1 otherwise it will return error message
    """
    Uid = session["Uid"]
    # check whether user is banned
    match_user: User = my_db.query(User, User.Uid == Uid, first=True)
    if match_user.banned:
        if match_user.banDuration > datetime.datetime.utcnow():
            return jsonify({"error": {"msg": "User banned."}, "status": 0})

    # verify post data in correct format
    Pid = request.form.get("Pid")
    content = request.form.get("content")
    if not Pid or not Pid.isnumeric() or not content:
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    # verify post exists
    match_post = my_db.query(Post, and_(Post.Pid == Pid, Post.status == 0), first=True)
    if not match_post:
        return jsonify({"error": {"msg": "Post not found."}, "status": 0})

    # verify text not too long
    text = request.form.get("text", "")  # can be None because comment may only contain photos and/or videos
    if len(text) > 1000:
        return jsonify({"error": {"msg": "Word count exceeded. Maximum: 1000"}, "status": 0})

    # make content HTML for parsing
    try:
        html = HTML(html=content)
    except Exception as e:
        return jsonify({"error": {"msg": e}, "status": 0})

    # fetch media list
    medias = []
    for ele in html.find("img.OT_image,iframe.OT_video"):
        src = ele.attrs.get("src")
        if src:
            tag = ele.tag
            path = PHOTO_PATH if tag == "img" else VIDEO_PATH
            medias.append(path + src.split("/")[-1])

    # check if the comment is replying other's comment
    reply_ele = html.find(".OT_reply", first=True)
    if reply_ele:
        ele_text_length = len(reply_ele.text)
        if len(text) <= ele_text_length and not medias:  # content is empty if not text nor media
            return jsonify({"error": {"msg": "Empty reply!"}, "status": 0})

        # retrieve receiver ID and target ID from data attributes (added by ourself) in HTML tag
        Rid = reply_ele.attrs["data-uid"]
        Tid = reply_ele.attrs["data-cid"]
        # if sender != receiver, send notification to comment owner
        if Uid != Rid:
            ntf_to_commenter = Notification("user", Uid, "user", Rid, "comment", Tid, "reply")
            my_db.add(ntf_to_commenter)

    # if sender != receiver, send notification to post owner
    if Uid != (Rid := match_post.owner.Uid):
        ntf_to_poster = Notification("user", Uid, "user", Rid, "post", Pid, "comment")
        my_db.add(ntf_to_poster)

    # record current available floor
    floor = match_post.available_floor
    # update post statistics
    match_post.available_floor += 1
    match_post.commentCount += 1
    match_post.latestCommentTime = datetime.datetime.utcnow()

    # add comment into database
    new_comment = Comment(Uid, Pid, content, floor, medias, text)
    my_db.add(new_comment)
    return jsonify({"status": 1})


@api.route('/post/delete', methods=["POST"])
@login_required
def delete_post():
    """
    THis function is used for logged in users to delete a post created by himself
    :return: if successful, it will redirect to the previous board
    otherwise, it will return json error message
    """
    Uid = session['Uid']

    Pid = request.form.get("Pid")
    if not Pid or not Pid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    match_post = my_db.query(Post, and_(Post.Pid == Pid, Post.Uid == Uid, Post.status == 0), first=True)
    if not match_post:
        return jsonify({"error": {"msg": "Post not found."}, "status": 0})

    match_post.under.postCount -= 1
    my_db.update(Post, Post.Pid == Pid, values={"status": 1})

    # Then delete all corresponding data in other relating tables
    for c in match_post.comments:
        my_db.update(Comment, Comment.Pid == c.Pid, values={"status": 1})

    return jsonify({"status": 1})


@api.route('/comment/delete', methods=["POST"])
@login_required
def delete_comment():  # will not alter post lastCommentTime
    """
    THis function is used for logged in users to delete a comment created by himself
    :return: if successful, it will redirect to the previous post
    otherwise, it will return json error message
    """
    Uid = session['Uid']

    Cid = request.form.get("Cid")
    if not Cid or not Cid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})
    match_comment = my_db.query(Comment, and_(Comment.Cid == Cid, Comment.Uid == Uid, Comment.status == 0), first=True)
    if not match_comment:
        return jsonify({"error": {"msg": "Comment not found."}, "status": 0})

    match_comment.comment_in.commentCount -= 1
    my_db.update(Comment, Comment.Cid == Cid, values={"status": 1})

    return jsonify({"status": 1})


@api.route('/post/restore', methods=["POST"])
@login_required
def restore_post():
    Uid = session['Uid']

    Pid = request.form.get("Pid")
    if not Pid or not Pid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    match_post = my_db.query(Post, and_(Post.Pid == Pid, Post.Uid == Uid, Post.status == 1), first=True)
    if not match_post:
        return jsonify({"error": {"msg": "Post not found."}, "status": 0})

    match_post.under.postCount += 1
    my_db.update(Post, Post.Pid == Pid, values={"status": 0})

    # Then restore all corresponding data in other relating tables
    for c in match_post.comments:
        my_db.update(Comment, Comment.Pid == c.Pid, values={"status": 0})

    return jsonify({"status": 1})


@api.route('/comment/restore', methods=["POST"])
@login_required
def restore_comment():
    Uid = session['Uid']

    Cid = request.form.get("Cid")
    if not Cid or not Cid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})
    match_comment = my_db.query(Comment, and_(Comment.Cid == Cid, Comment.Uid == Uid, Comment.status == 1), first=True)
    if not match_comment:
        return jsonify({"error": {"msg": "Comment not found."}, "status": 0})

    match_comment.comment_in.commentCount += 1
    my_db.update(Comment, Comment.Cid == Cid, values={"status": 0})

    return jsonify({"status": 1})


@api.route('/personal_info/add', methods=["POST"])
@login_required
def add_personal_info():
    """
    This function is used for logged in users to add information in their profile
    :return: if successful, it will redirect to the profile page of this user
    otherwise, it will return json error message
    """
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
    """
    This function is to evaluate the registration
    :return: json information:
    if the registration is successful it will return status 1 otherwise it will return error message
    """
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
    session["last_check"] = new_user.lastCheck
    return jsonify({"status": 1})


@api.route('/auth/login', methods=["POST"])
def login_auth():
    """
    This function is to evaluate the log in
    :return: json information:
    if the log in is successful it will return status 1 and corresponding Uid otherwise it will return error message
    """
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
    session["last_check"] = match_user.lastCheck
    # session.permanent = True
    return jsonify({"status": 1, "Uid": match_user.Uid})


@api.route('/auth/logout', methods=["POST", "GET"])
@login_required
def logout_auth():
    """
    This function is used for logged in user to logout
    :return: a html text message
    """
    session.clear()
    return "<script>location.replace(document.referrer);</script>", 200


@api.route("/upload", methods=["POST", "GET"])
def handle_upload():
    """
    This function is used for users to upload their avatar, image or video
    :return: if this user is not logged in, it will redirect to the log in page
    if the uploading failed, it will return json error message
    """
    action = request.args.get("action")
    method = request.method.upper()

    if action == "uploadavatar" and method == "POST":  # user action. Upload avatar
        if not session.get("Uid"):
            return redirect("/login")

        Uid = session["Uid"]
        file = request.files.get("file")
        # check if file
        if not file:
            return jsonify({"error": {"msg": "Please upload a file"}})
        # check file type
        file_type = file.content_type
        if not file_type or not file_type.startswith("image"):
            return jsonify({"error": {"msg": "Invalid file type"}})
        file_type = file_type.split("/")[-1]
        # check file size
        file_size = int(request.headers.get("Content-Length", 0))
        if file_size > 3 * 1024 * 1024:
            return jsonify({"error": {"msg": "Image too large"}})

        path = CDN_ROOT_PATH + AVATAR_PATH
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

        new_avatar = AVATAR_PATH + src
        my_db.update(User, User.Uid == Uid, values={"avatar": new_avatar})
        session.pop("user_info")
        session["user_info"] = {"nickname": match_user.nickname, "avatar": new_avatar}
        result = {"status": 1}

    elif action == "config" and method == "GET":  # ueditor action. Config the ueditor, user may not be logged-in
        with open("ourtieba/static/ueditor/config.json", "r") as f:
            content = f.read()
        result = json.loads(content)

    elif action == "uploadimage" and method == "POST":  # ueditor + user action. Upload photo within post and comment
        if not session.get("Uid"):
            return jsonify({"error": {"msg": "Not logged in"}, "status": 0})  # AE: can be any error, ignored by ueditor
        Uid = session["Uid"]

        file = request.files.get("upfile")
        file_type = file.content_type
        if not file_type or not file_type.startswith("image"):
            return jsonify({"error": {"msg": "Invalid file type"}})
        file_type = file_type.split("/")[-1]

        file_size = int(request.headers.get("Content-Length", 0))
        if file_size > 2048000:  # must be the same as in static/ueditor/config.json ("imageMaxSize")
            return jsonify({"error": {"msg": "Not logged in"}, "status": 0})  # AE

        path = CDN_ROOT_PATH + PHOTO_PATH
        if not os.path.exists(path):  # os is imported in config.py
            os.mkdir(path)

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

    elif action == "uploadvideo" and method == "POST":  # ueditor + user action. Upload video within post and comment
        if not session.get("Uid"):
            return jsonify({"error": {"msg": "Not logged in"}, "status": 0})
        Uid = session["Uid"]

        file = request.files.get("upfile")
        file_type = file.content_type
        if not file_type or not file_type.startswith("video"):
            return jsonify({"error": {"msg": "Invalid file type"}})
        file_type = file_type.split("/")[-1]

        file_size = int(request.headers.get("Content-Length", 0))
        if file_size > 102400000:  # must be the same as in static/ueditor/config.json ("videoMaxSize")
            return jsonify({"error": {"msg": "Not logged in"}, "status": 0})  # AE

        path = CDN_ROOT_PATH + VIDEO_PATH
        if not os.path.exists(path):  # os is imported in config.py
            os.mkdir(path)

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
        result = {"error": {"msg": "Something went wrong"}, "status": 0}
    return jsonify(result)


@api.route("/subscribe", methods=["POST"])
@login_required
def subscribe():
    """
    This function is used for logged in users to subscribe a board
    :return: json information
    if the subscribe is successful it will return status 1 otherwise it will return error message
    """
    Uid = session["Uid"]

    Bid = request.form.get("Bid")
    action = request.form.get("action")  # "0"=unsub, "1"=sub
    if not Bid or not Bid.isnumeric() or action not in ("0", "1"):
        return jsonify({"error": {"msg": "invalid data"}, "status": 0})

    match_board = my_db.query(Board, Board.Bid == Bid, first=True)
    if not match_board:
        return jsonify({"error": {"msg": "invalid board ID"}, "status": 0})
    if match_board.status != 0:
        return jsonify({"error": {"msg": "Board not exists"}, "status": 0})
    match_board.subscribeCount += 1 if action == "1" else -1

    new_sub = Subscription(Uid, Bid, int(action), lastModified=datetime.datetime.utcnow())
    my_db.merge(new_sub)
    return jsonify({"subs_count": match_board.subscribeCount, "status": 1})


@api.route("/auth/set_password")
@login_required
def set_password():
    """
    This function is used for logged in users to evaluate password setting process
    :return: json information
    if the setting is successful it will return status 1 otherwise it will return error message
    """
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


@api.route("/fetch")
def fetch_data():
    cur_Uid = session.get("Uid", 0)
    # Optional: Can block user's request when cur_Uid != session["Uid"] (the user is viewing other's profile)

    Uid = request.args.get("Uid")
    type_data = request.args.get("type")

    if not Uid or not type_data or not type_data.isnumeric() or not (0 <= (type_data := int(type_data)) <= 3):
        return jsonify({"error": {"msg": "Invalid data!"}, "status": 0})

    match_user = my_db.query(User, User.Uid == Uid, first=True)
    if not match_user:
        return jsonify({"error": {"msg": "No user found!"}, "status": 0})

    base_info = {"status": 1}

    if type_data == 0:
        post_info = [{"Pid": p.Pid, "Bid": p.Bid, "bname": p.under.name, "title": p.title,
                      "timestamp": p.timestamp, "status": p.status} for p in match_user.posts]
        # sort by timestamp desc
        post_info.sort(key=lambda p: p["timestamp"], reverse=True)
        # convert times into shorter format
        for p in post_info:
            p["timestamp"] = convert_time(p["timestamp"])
        base_info.update({"info": post_info, "count": len(post_info)})
    elif type_data == 3:
        history_info = []
        for h in match_user.view:
            history = {"Pid": h.Pid, "LVT": h.lastVisitTime}
            p = h.related_post
            history.update({"title": p.title, "bname": p.under.name, "Bid": p.Bid, "Uid": (u := p.owner).Uid,
                            "nickname": u.nickname, "me": int(u.Uid == cur_Uid),
                            "status": p.status})  # "me" = whether post by me
            history_info.append(history)
        # sort by LVT desc
        history_info.sort(key=lambda ht: ht["LVT"], reverse=True)
        # convert times into shorter format
        for h in history_info:
            h["LVT"] = convert_time(h["LVT"])
        base_info.update({"info": history_info, "count": len(history_info)})
    elif type_data == 2:
        subs_info = []
        for s in match_user.subscriptions:
            if s.subscribed == 1:
                if (b := s.of_board).status == 0:
                    subs_info.append({"Bid": s.Bid, "bname": b.name, "LM": s.lastModified,
                                      "cover": b.cover, "status": 0})
        # sort by LM desc
        subs_info.sort(key=lambda sb: sb["LM"], reverse=True)
        base_info.update({"info": subs_info, "count": len(subs_info)})
    else:
        comment_info = []
        for c in match_user.comments:
            comment = {"Cid": c.Cid, "text": c.text, "timestamp": c.timestamp, "status": c.status}
            p = c.comment_in
            comment.update({"Pid": p.Pid, "title": p.title})
            comment_info.append(comment)
        # sort by timestamp desc
        comment_info.sort(key=lambda ci: ci["timestamp"], reverse=True)
        # convert times into shorter format
        for c in comment_info:
            c["timestamp"] = convert_time(c["timestamp"])
        base_info.update({"info": comment_info, "count": len(comment_info)})

    return jsonify(base_info)


@api.route("/get_log")
def get_log():
    Uid = session.get("Uid")
    last_check = session.get("last_check")
    if not Uid or not last_check:
        return jsonify({"code": -1})
    cur_ts = request.args.get("t") or time.time()  # can be used for synchronization given FIFO channel
    new_count = my_db.count(Notification, and_(Notification.receiver == "user", Notification.Rid == Uid,
                                               Notification.timestamp.between(last_check, cur_ts)))
    if not new_count:
        return jsonify({"code": 204})  # empty response
    return jsonify({"code": 200, "new_count": new_count})
