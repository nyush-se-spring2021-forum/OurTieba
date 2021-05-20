import json
import time

from flask import Blueprint, jsonify, request
from requests_html import HTML

from ..configs import *
from ..database import *
from ..html_parser import *
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
    if User.is_banned(Uid):
        return jsonify({"error": {"msg": "You are banned."}, "status": 0})

    Bid = request.form.get("Bid")
    title = request.form.get("title")
    if not Bid or not Bid.isnumeric() or not title:
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    if len(title) > 150:
        return jsonify({"error": {"msg": "Title word count exceeded. Maximum: 150"}, "status": 0})

    if not Board.action_on_post(Bid, 0):
        return jsonify({"error": {"msg": "Board not found."}, "status": 0})

    content = request.form.get("content", "<p></p>")
    text = request.form.get("text", "")
    if not content:  # unknown bug, the get above does not work
        content = "<p></p>"

    if len(text) > 2000:
        return jsonify({"error": {"msg": "Content word count exceeded. Maximum: 2000"}, "status": 0})

    content = my_parser.clean(content)
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

    Post.new(Uid, int(Bid), title, content, medias, text)
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
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    if target == "comment":
        info = Comment.like(target_id, Uid)
    else:
        info = Post.like(target_id, Uid)
    if info == 0:
        return jsonify({"error": {"msg": "Invalid target ID."}, "status": 0})
    if info == -1:
        return jsonify({"error": {"msg": "Target not exists."}, "status": 0})

    # Check whether the user likes his own target
    if Uid != info[-1]:
        Notification.new("user", Uid, "user", info[-1], target, target_id, "like", time.time())
    return jsonify({"cur_status": info[0], "like_count": info[1], "dislike_count": info[2], "status": 1})

    # query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
    #     Post, Post.Pid == target_id)
    # match_target = query_from._query(filter_cond, first=True)
    # # match_target = my_db.query(query_from, filter_cond, first=True)
    # if not match_target:
    #     return jsonify({"error": {"msg": "Invalid target ID."}, "status": 0})
    # if match_target.status != 0:
    #     return jsonify({"error": {"msg": "Target not exists."}, "status": 0})
    #
    # status = CommentStatus if target == "comment" else PostStatus
    # status_cond = CommentStatus.Cid == target_id if target == "comment" else PostStatus.Pid == target_id
    # match_status = status._query(and_(status.Uid == Uid, status_cond), first=True)
    # # match_status = my_db.query(status, and_(status.Uid == Uid, status_cond), first=True)
    #
    # if not match_status:
    #     cur_status = 1
    #     status.new(Uid, int(target_id), cur_status, 0)
    #     # new_status = status(Uid, int(target_id), cur_status, 0)
    #     # my_db.add(new_status)
    #     match_target.likeCount += 1
    # else:
    #     liked = match_status.liked
    #     disliked = match_status.disliked
    #     cur_status = 0 if liked else 1
    #     new_status = status(Uid, int(target_id), cur_status, 0, datetime.datetime.utcnow())
    #     ###Need to be more clear
    #     my_db.merge(new_status)
    #     match_target.likeCount += -1 if liked else 1
    #     match_target.dislikeCount -= 1 if disliked else 0
    #
    # cur_target = query_from._query(filter_cond, first=True)
    # # cur_target = my_db.query(query_from, filter_cond, first=True)
    # cur_like, cur_dislike = cur_target.likeCount, cur_target.dislikeCount


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
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    if target == "comment":
        info = Comment.dislike(target_id, Uid)
    else:
        info = Post.dislike(target_id, Uid)
    if info == 0:
        return jsonify({"error": {"msg": "Invalid target ID."}, "status": 0})
    if info == -1:
        return jsonify({"error": {"msg": "Target not exists."}, "status": 0})

    # Check whether the user is dislike his own target
    if Uid != info[-1]:
        Notification.new("user", Uid, "user", info[-1], target, target_id, "like", time.time())
    return jsonify({"cur_status": info[0], "like_count": info[1], "dislike_count": info[2], "status": 1})

    # query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
    #     Post, Post.Pid == target_id)
    # match_target = query_from._query(filter_cond, first=True)
    # # match_target = my_db.query(query_from, filter_cond, first=True)
    # if not match_target:
    #     return jsonify({"error": {"msg": "Invalid target ID."}, "status": 0})
    # if match_target.status != 0:
    #     return jsonify({"error": {"msg": "Target not exists."}, "status": 0})
    #
    # status = CommentStatus if target == "comment" else PostStatus
    # status_cond = CommentStatus.Cid == target_id if target == "comment" else PostStatus.Pid == target_id
    # match_status = status._query(and_(status.Uid == Uid, status_cond), first=True)
    # # match_status = my_db.query(status, and_(status.Uid == Uid, status_cond), first=True)
    #
    # if not match_status:
    #     cur_status = 1
    #     status.new(Uid, int(target_id), 0, 1)
    #     # new_status = status(Uid, int(target_id), 0, 1)
    #     # my_db.add(new_status)
    #     match_target.dislikeCount += 1
    # else:
    #     liked = match_status.liked
    #     disliked = match_status.disliked
    #     cur_status = 0 if disliked else 1
    #     new_status = status(Uid, int(target_id), 0, cur_status, datetime.datetime.utcnow())
    #     # Need to be more clear
    #     my_db.merge(new_status)
    #     match_target.dislikeCount += -1 if disliked else 1
    #     match_target.likeCount -= 1 if liked else 0
    #
    # cur_target = query_from._query(filter_cond, first=True)
    # # cur_target = my_db.query(query_from, filter_cond, first=True)
    # cur_like, cur_dislike = cur_target.likeCount, cur_target.dislikeCount
    # return jsonify({"cur_status": cur_status, "like_count": cur_like, "dislike_count": cur_dislike, "status": 1})


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

    if User.is_banned(Uid):
        return jsonify({"error": {"msg": "You are banned."}, "status": 0})
    if target not in ["comment", "post"] or not target_id or not target_id.isnumeric() or not reason:
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    reason = my_parser.clean(reason)

    if target == "comment":
        message = Comment.report(Uid, target_id, reason)
    else:
        message = Post.report(Uid, target_id, reason)
    return jsonify(message)

    # query_from, filter_cond = (Comment, Comment.Cid == target_id) if target == "comment" else (
    #     Post, Post.Pid == target_id)
    # match_target = query_from._query(filter_cond, first=True)
    # # match_target = my_db.query(query_from, filter_cond, first=True)
    # if not match_target:
    #     return jsonify({"error": {"msg": "Invalid target ID."}, "status": 0})
    #
    # Pid = match_target.Pid
    # # insert into db
    # Report.new(Uid, target, int(target_id), reason)
    # new_report = Report(Uid, target, int(target_id), reason)
    # # my_db.add(new_report)
    #
    # reporter = User._query(User.Uid == Uid, first=True)
    # # reporter = my_db.query(User, User.Uid == Uid, first=True)
    # reporter.reports.append(new_report)
    # return jsonify({"status": 1})


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
    if User.is_banned(Uid):
        return jsonify({"error": {"msg": "You are banned."}, "status": 0})

    # verify post data in correct format
    Pid = request.form.get("Pid")
    content = request.form.get("content")
    if not Pid or not Pid.isnumeric() or not content:
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    # filter content
    content = my_parser.clean(content)

    # verify post exists
    match_post = Post._query((Post.Pid == Pid and Post.status == 0), first=True)
    # match_post = my_db.query(Post, and_(Post.Pid == Pid, Post.status == 0), first=True)
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
    floor = Post.add_comment(Pid, Uid, reply_ele, text, medias)
    if floor == 0:
        return jsonify({"error": {"msg": "Post not found."}, "status": 0})
    if floor == -1:
        return jsonify({"error": {"msg": "Empty reply!"}, "status": 0})

    # add comment into database
    Comment.new(Uid, Pid, content, floor, medias, text)
    # new_comment = Comment(Uid, Pid, content, floor, medias, text)
    # my_db.add(new_comment)
    return jsonify({"status": 1})


@api.route('/post/delete', methods=["POST"])
@login_required
def delete_post():
    """
    THis function is used for logged in users to delete a post created by himself
    :return: if successful, it will redirect to the previous board
    otherwise, it will return json error message
    """
    Pid = request.form.get("Pid")
    if not Pid or not Pid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    Uid = Post.delete_post(Pid)
    if Uid == 0:
        return jsonify({"error": {"msg": "Post not found."}, "status": 0})
    return jsonify({'status': 1})


@api.route('/comment/delete', methods=["POST"])
@login_required
def delete_comment():  # will not alter post lastCommentTime
    """
    THis function is used for logged in users to delete a comment created by himself
    :return: if successful, it will redirect to the previous post
    otherwise, it will return json error message
    """
    Cid = request.form.get("Cid")
    if not Cid or not Cid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    Uid = Comment.delete_comment(Cid)
    if Uid == 0:
        return jsonify({"error": {"msg": "Comment not found."}, "status": 0})
    return jsonify({'status': 1})


@api.route('/post/restore', methods=["POST"])
@login_required
def restore_post():
    Pid = request.form.get("Pid")
    if not Pid or not Pid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    Uid = Post.restore_post(Pid, "user")
    if Uid == 0:
        return jsonify({"error": {"msg": "Post not found."}, "status": 0})
    return jsonify({'status': 1})


@api.route('/comment/restore', methods=["POST"])
@login_required
def restore_comment():
    Cid = request.form.get("Cid")
    if not Cid or not Cid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    Uid = Comment.restore_comment(Cid, "user")
    if Uid == 0:
        return jsonify({"error": {"msg": "Comment not found."}, "status": 0})
    return jsonify({'status': 1})


@api.route('/personal_info/add', methods=["POST"])
@login_required
def add_personal_info():
    """
    This function is used for logged in users to add information in their profile. They can choose to only update
    part of it.
    :return: if successful, it will redirect to the profile page of this user
    otherwise, it will return json error message
    """
    Uid = session["Uid"]
    values = {}

    nickname = request.form.get("nickname")
    if len(nickname) > 20:
        return jsonify({"error": {"msg": "Nickname too long."}, "status": 0})
    if nickname != "":
        values.update({"nickname": nickname})
    # check gender
    gender = request.form.get("gender")
    if gender != "" and gender not in ("male", "female", "other"):
        return jsonify({"error": {"msg": "Invalid gender."}, "status": 0})
    if gender != "":
        values.update({"gender": gender})
    # check phone number
    phone_number = request.form.get("phone_number")
    if phone_number != "":
        phone_number = re.findall(r"^[+]*[(]?[0-9]{1,4}[)]?[-\s./0-9]*$", phone_number)
        if not phone_number:
            return jsonify({"error": {"msg": "Invalid phone number."}, "status": 0})
        else:
            phone_number = phone_number[0]
            values.update({"phoneNumber": phone_number})
    # check email
    email = request.form.get("email")
    if email != "":
        email = re.findall(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)
        if not email:
            return jsonify({"error": {"msg": "Invalid email."}, "status": 0})
        else:
            email = email[0]
            values.update({"email": email})
    # check address
    address = request.form.get("address")
    if address != "" and len(address) > 200:
        return jsonify({"error": {"msg": "Address too long."}, "status": 0})
    if address != "":
        values.update({"address": address})
    # check date of birth
    date_of_birth = request.form.get("date_of_birth")
    if date_of_birth != "":
        try:
            date_of_birth = datetime.datetime.strptime(date_of_birth, "%Y-%m-%d")
        except Exception as e:
            return jsonify({"error": {"msg": f"Invalid date of birth: {e}."}, "status": 0})
        values.update({"dateOfBirth": date_of_birth})

    nickname, avatar = User.add_personal_info(Uid, values)
    # match_user = my_db.query(User, User.Uid == Uid, first=True)
    session.pop("user_info")
    session["user_info"] = {"nickname": nickname, "avatar": avatar}
    return jsonify({"status": 1})


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
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})
    # (validity)
    username = re.findall(r"[\w_]+$", username)
    if not username:
        return jsonify({"error": {"msg": "Invalid username."}, "status": 0})
    else:
        username = username[0]
    if len(username) < 5 or len(username) > 20:
        return jsonify({"error": {"msg": "Username must be of length 5 ~ 20."}, "status": 0})
    # check password
    password = request.form.get("password")
    if not password:
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})
    password = re.findall(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", password)
    if not password:
        return jsonify({"error": {"msg": "Invalid password."}, "status": 0})
    else:
        password = password[0]
    # check nickname
    nickname = request.form.get("nickname")
    if not nickname or len(nickname) > 20:
        return jsonify({"error": {"msg": "Invalid nickname."}, "status": 0})

    info = User.register_auth(password, username, nickname)
    if info == 0:
        return jsonify({"error": {"msg": "User already exists."}, "status": 0})

    session["Uid"] = info[0]
    session["user_info"] = {"nickname": info[1], "avatar": info[2]}
    session["last_check"] = info[3]
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

    info = User.login_auth(username, password)
    if info == 0:
        return jsonify({"error": {"msg": "Username does not exist."}, "status": 0})
    if info == 1:
        return jsonify({"error": {"msg": "Incorrect password."}, "status": 0})
    session["Uid"] = info[0]
    user_info = {"nickname": info[1], "avatar": info[2]}
    session["user_info"] = user_info
    session["last_check"] = info[3]
    # session.permanent = True
    return jsonify({"status": 1, "Uid": info[0]})


@api.route('/auth/logout', methods=["POST"])
@login_required
def logout_auth():
    """
    This function is used for logged in user to logout. Clear all session data
    :return: if successful return status 1
    """
    session.clear()
    return jsonify({"status": 1})


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
            return jsonify({"error": {"msg": "Please upload a file."}, "status": 0})
        # check file type
        file_type = file.content_type
        if not file_type or not file_type.startswith("image"):
            return jsonify({"error": {"msg": "Invalid file type."}, "status": 0})
        file_type = file_type.split("/")[-1]
        # check file size
        file_size = int(request.headers.get("Content-Length", 0))
        if file_size > 3 * 1024 * 1024:
            return jsonify({"error": {"msg": "Image too large."}, "status": 0})

        path = CDN_ROOT_PATH + AVATAR_PATH
        if not os.path.exists(path):  # os is imported in config.py
            os.mkdir(path)

        src = str(hash(str(Uid) + str(datetime.datetime.utcnow()))) + "." + file_type
        filepath = path + src
        while os.path.exists(filepath):
            src = str(hash(str(Uid) + str(datetime.datetime.utcnow()))) + "." + file_type
            filepath = path + src
        file.save(filepath)

        avatar = User.get_avatar(Uid)
        if avatar != "default_avatar.jpg":
            old_path = path + avatar
            if os.path.exists(old_path):
                os.remove(old_path)

        new_avatar = AVATAR_PATH + src
        nickname, avatar_path = User.change_avatar(Uid, new_avatar)
        session.pop("user_info")
        session["user_info"] = {"nickname": nickname, "avatar":avatar_path}
        result = {"status": 1}

    elif action == "config" and method == "GET":  # ueditor action. Config the ueditor, user may not be logged-in
        with open("ourtieba/static/ueditor/config.json", "r") as f:
            content = f.read()
        result = json.loads(content)

    elif action == "uploadimage" and method == "POST":  # ueditor + user action. Upload photo within post and comment
        if not session.get("Uid"):
            return jsonify(
                {"error": {"msg": "Not logged in."}, "status": 0})  # AE: can be any error, ignored by ueditor
        Uid = session["Uid"]

        file = request.files.get("upfile")
        if not file:
            return jsonify({"error": {"msg": "Please upload a file."}, "status": 0})
        file_type = file.content_type
        if not file_type or not file_type.startswith("image"):
            return jsonify({"error": {"msg": "Invalid file type."}, "status": 0})
        file_type = file_type.split("/")[-1]

        file_size = int(request.headers.get("Content-Length", 0))
        if file_size > 2048000:  # must be the same as in static/ueditor/config.json ("imageMaxSize")
            return jsonify({"error": {"msg": "File too large."}, "status": 0})  # AE

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
            return jsonify({"error": {"msg": "Not logged in."}, "status": 0})
        Uid = session["Uid"]

        file = request.files.get("upfile")
        if not file:
            return jsonify({"error": {"msg": "Please upload a file."}, "status": 0})
        file_type = file.content_type
        if not file_type or not file_type.startswith("video"):
            return jsonify({"error": {"msg": "Invalid file type."}, "status": 0})
        file_type = file_type.split("/")[-1]

        file_size = int(request.headers.get("Content-Length", 0))
        if file_size > 102400000:  # must be the same as in static/ueditor/config.json ("videoMaxSize")
            return jsonify({"error": {"msg": "File too large."}, "status": 0})  # AE

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
        result = {"error": {"msg": "Something went wrong."}, "status": 0}
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
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    if not Board.exists(Bid):
        return jsonify({"error": {"msg": "Board not found."}, "status": 0})

    update = Subscription.needs_update(Uid, Bid, (action := int(action)))
    subs_count = Board.action_on_subs(Bid, update)
    Subscription.merge(Uid, Bid, action, lastModified=datetime.datetime.utcnow())
    return jsonify({"subs_count": subs_count, "status": 1})


@api.route("/fetch")
def fetch_data():
    cur_Uid = session.get("Uid", 0)
    # Optional: Can block user's request when cur_Uid != session["Uid"] (the user is viewing other's profile)

    Uid = request.args.get("Uid")
    type_data = request.args.get("type")

    if not Uid or not type_data or not type_data.isnumeric() or not (0 <= (type_data := int(type_data)) <= 3):
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    if not User.exists(Uid):
        return jsonify({"error": {"msg": "User not found."}, "status": 0})

    base_info = {"status": 1}

    if type_data == 0:
        post_info_list = User.get_post_info_list(Uid)
        # sort by timestamp desc
        post_info_list.sort(key=lambda pi: pi["timestamp"], reverse=True)
        # convert times into shorter format
        for p in post_info_list:
            p["timestamp"] = convert_time(p["timestamp"])
        base_info.update({"info": post_info_list, "count": len(post_info_list)})
    elif type_data == 1:
        comment_info_list = User.get_comment_info_list(Uid)
        # sort by timestamp desc
        comment_info_list.sort(key=lambda ci: ci["timestamp"], reverse=True)
        # convert times into shorter format
        for c in comment_info_list:
            c["timestamp"] = convert_time(c["timestamp"])
        base_info.update({"info": comment_info_list, "count": len(comment_info_list)})
    elif type_data == 2:
        subs_info_list = User.get_subs_info_list(Uid)
        # sort by LM desc
        subs_info_list.sort(key=lambda sb: sb["LM"], reverse=True)
        base_info.update({"info": subs_info_list, "count": len(subs_info_list)})
    else:  # if type_data == 3
        history_info_list = User.get_history_info_list(Uid, cur_Uid)
        # sort by LVT desc
        history_info_list.sort(key=lambda ht: ht["LVT"], reverse=True)
        # convert times into shorter format
        for h in history_info_list:
            h["LVT"] = convert_time(h["LVT"])
        base_info.update({"info": history_info_list, "count": len(history_info_list)})
    return jsonify(base_info)


@api.route("/get_log")
def get_log():
    Uid = session.get("Uid")
    last_check = session.get("last_check")
    if not Uid or not last_check:
        return jsonify({"code": -1})
    cur_ts = request.args.get("t") or time.time()  # can be used for synchronization given FIFO channel
    new_count = Notification.get_count_between(Uid, last_check, cur_ts)
    if not new_count:
        return jsonify({"code": 204})  # empty response
    return jsonify({"code": 200, "new_count": new_count})


@api.route("/get_ntf")
@login_required
def fetch_ntf():
    Uid = session["Uid"]
    last_check = session["last_check"]
    cur_ts = time.time()

    end = request.args.get("end")  # cursor end
    if end is None or not end.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})
    end = int(end)
    limit = 10  # IMPORTANT: how many ntfs to fetch every time

    cls_dict = {"user": User, "admin": Admin, "post": Post, "comment": Comment, "board": Board}
    ntfs = Notification.compose_ntfs(cls_dict, Uid, Notification.timestamp.desc(), limit, end, last_check)
    if end == 0:  # update last check, however in this way at most 10 ntfs can be "is_new",
        # to fix it, need to modify database, but I do not intend to do this
        User.update(User.Uid == Uid, values={"lastCheck": cur_ts})
        session["last_check"] = cur_ts
    end += len(ntfs)
    is_end = 1 if len(ntfs) < limit else 0
    return jsonify({"cursor_end": end, "is_end": is_end, "ntfs": ntfs, "status": 1})
