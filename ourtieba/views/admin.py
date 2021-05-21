import hashlib
import time

from flask import Blueprint, jsonify, render_template, request

from ..configs import *
from ..models import *

admin_blue = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blue.route("/")
def admin_hello():
    """
    This function is used to redirect to admin dashboard
    :return: redirect to another path of '/admin/dashboard'
    """
    return redirect("/admin/dashboard")


@admin_blue.route("/login")
def admin_login():
    """
    This function is used to show the admin login page
    :return: admin_login.html
    """
    return render_template("admin_login.html")


@admin_blue.route("/dashboard")
@admin_login_required
def admin_dashboard():
    """
    This function is used for logged admins to show their dashboard
    :return: admin_dashboard.html
    """
    page = request.args.get("page", "1")
    order = Report.timestamp.desc()

    num_reports = Report.count_unresolved_reports()
    num_page = (num_reports - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    reports = Report.get_unresolved_reports_info_by_page(page, PAGE_SIZE, order)
    data = {"num_match": num_reports, "num_page": num_page, "page": page, "reports": reports}
    return render_template("admin_dashboard.html", data=data)


@admin_blue.route("/auth/login", methods=["POST"])
def admin_auth_login():
    """
    This function is to evaluate the process of login of the admins
    :return: json information
    if the process is successful it will return status 1 otherwise it will return error message
    """
    aname = request.form.get("aname")
    password = request.form.get("password")
    if not aname or not password:
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    admin_info = Admin.get_info_by_name(aname)
    if not admin_info:
        return jsonify({"error": {"msg": "Admin not found."}, 'status': 0})
    encoded_password = hashlib.sha3_512(password.encode()).hexdigest()
    recorded_password = admin_info["password"]
    if encoded_password != recorded_password:
        return jsonify({"error": {"msg": "Incorrect password."}, 'status': 0})

    session["Aid"] = admin_info["Aid"]
    admin_session = {"nickname": admin_info["nickname"], "avatar": admin_info["avatar"]}
    session["admin_info"] = admin_session
    # session.permanent = True
    return jsonify({'status': 1})


@admin_blue.route("/auth/logout", methods=["POST"])
@admin_login_required
def admin_logout():
    """
    This function is used for logged in admins to logout
    :return: redirect to another path of '/admin/login'
    """
    session.clear()
    return jsonify({"status": 1})


@admin_blue.route("/board/delete", methods=["POST"])
@admin_login_required
def admin_board_delete():
    """
    This function is used for logged in admin to delete a board
    :return: json information
    if the deletion is successful it will return status 1 otherwise it will return error message
    """
    Bid = request.form.get("Bid")
    if not Bid or not Bid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    message = Board.ban_board(Bid)
    return jsonify(message)


@admin_blue.route("/post/delete", methods=["POST"])
@admin_login_required
def admin_post_delete():
    """
    This function is used for logged in admin to delete a post
    :return: json information
    if the deletion is successful it will return status 1 otherwise it will return error message
    """
    Pid = request.form.get("Pid")
    if not Pid or not Pid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    Uid = Post.ban_post(Pid)
    if Uid == 0:
        return jsonify({"error": {"msg": "Post not found."}, "status": 0})
    Notification.new("admin", session["Aid"], "user", Uid, "post", Pid, "delete", time.time())
    return jsonify({'status': 1})


@admin_blue.route("/comment/delete", methods=["POST"])
@admin_login_required
def admin_comment_delete():
    """
    This function is used for logged in admin to delete a comment
    :return: json information
    if the deletion is successful it will return status 1 otherwise it will return error message
    """
    Cid = request.form.get("Cid")
    if not Cid or not Cid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    Uid = Comment.ban_comment(Cid)
    if Uid == 0:
        return jsonify({"error": {"msg": "Comment not found."}, "status": 0})
    Notification.new("admin", session["Aid"], "user", Uid, "comment", Cid, "delete", time.time())
    return jsonify({'status': 1})


@admin_blue.route("/board/restore", methods=["POST"])
@admin_login_required
def admin_board_restore():
    """
    This function is used for logged in admin to delete a board
    :return: json information
    if the deletion is successful it will return status 1 otherwise it will return error message
    """
    Bid = request.form.get("Bid")
    if not Bid or not Bid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    message = Board.restore_board(Bid, "admin")
    return jsonify(message)


@admin_blue.route("/post/restore", methods=["POST"])
@admin_login_required
def admin_post_restore():
    """
    This function is used for logged in admin to delete a post
    :return: json information
    if the deletion is successful it will return status 1 otherwise it will return error message
    """
    Pid = request.form.get("Pid")
    if not Pid or not Pid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    Uid = Post.restore_post(Pid, "admin")
    if Uid == 0:
        return jsonify({"error": {"msg": "Post not found."}, "status": 0})
    Notification.new("admin", session["Aid"], "user", Uid, "post", Pid, "restore", time.time())
    return jsonify({'status': 1})


@admin_blue.route("/comment/restore", methods=["POST"])
@admin_login_required
def admin_comment_restore():
    """
    This function is used for logged in admin to delete a comment
    :return: json information
    if the deletion is successful it will return status 1 otherwise it will return error message
    """
    Cid = request.form.get("Cid")
    if not Cid or not Cid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    Uid = Comment.restore_comment(Cid, "admin")
    if Uid == 0:
        return jsonify({"error": {"msg": "Comment not found."}, "status": 0})
    Notification.new("admin", session["Aid"], "user", Uid, "comment", Cid, "restore", time.time())
    return jsonify({'status': 1})


@admin_blue.route("/user/ban", methods=["POST"])
@admin_login_required
def admin_user_ban():
    """
    This function is used for logged in admin to ban a user
    :return: json information
    if the ban is successful it will return status 1 otherwise it will return error message
    """
    Uid = request.form.get("Uid")
    days = request.form.get("days")
    if not Uid or not Uid.isnumeric() or not days or not days.isnumeric() or int(days) <= 0:
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    message = User.ban(Uid, days)
    Notification.new("admin", session["Aid"], "user", Uid, "user", int(days), "ban", time.time())
    return jsonify(message)


@admin_blue.route("/user/unban", methods=["POST"])
@admin_login_required
def admin_user_unban():
    """
    This function is user for logged in admin to unban a user
    :return: json information
    if the ban is successful it will return status 1 otherwise it will return error message
    """
    Uid = request.form.get("Uid")
    if not Uid or not Uid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    message = User.unban(Uid)
    Notification.new("admin", session["Aid"], "user", Uid, "user", 0, "unban", time.time())
    return jsonify(message)


@admin_blue.route("/report/resolve", methods=["POST"])
@admin_login_required
def admin_report_resolve():
    """
    This function is used for logged in admin to resolve a report
    :return: json information
    if the process of resolution is successful it will return status 1 otherwise it will return error message
    """
    Rid = request.form.get("Rid")
    if not Rid or not Rid.isnumeric():
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})

    message = Report.resolve(Rid)
    return jsonify(message)


@admin_blue.route("/create")
@admin_login_required
def create_board_interface():
    return render_template("create_board.html")


@admin_blue.route("/board/add", methods=["POST"])
@admin_login_required
def add_board_by_admin():
    name = request.form.get("name")
    description = request.form.get("description")
    cover = request.form.get("cover", "cover/OurTieba.png")
    if not name or not description:
        return jsonify({"error": {"msg": "Invalid data."}, "status": 0})
    if len(name) > 40:
        return jsonify({"error": {"msg": "Name word count exceeded. Maximum: 40"}, "status": 0})
    if len(description) > 200:
        return jsonify({"error": {"msg": "Description word count exceeded. Maximum: 200"}, "status": 0})
    if Board.name_exists(name):
        return jsonify({"error": {"msg": "Board name already exists."}, "status": 0})
    Board.new(name, description, cover=cover)
    return jsonify({'status': 1})


@admin_blue.route("/upload", methods=["POST"])
@admin_login_required
def upload_by_admin():
    action = request.args.get("action")
    if action != "uploadcover":
        return jsonify({"error": {"msg": "Wrong action."}, "status": 0})

    Aid = session["Aid"]

    file = request.files.get("file")
    file_type = file.content_type
    if not file_type or not file_type.startswith("image"):
        return jsonify({"error": {"msg": "Invalid file type.", "status": 0}})
    file_type = file_type.split("/")[-1]

    file_size = int(request.headers.get("Content-Length", 0))
    if file_size > 3 * 1024 * 1024:
        return jsonify({"error": {"msg": "Cover size too large."}, "status": 0})

    path = CDN_ROOT_PATH + COVER_PATH
    if not os.path.exists(path):  # os is imported in config.py
        os.mkdir(path)

    src = str(hash(str(Aid) + str(datetime.datetime.utcnow()))) + "." + file_type
    while os.path.exists((filepath := path + src)):
        src = str(hash(str(Aid) + str(datetime.datetime.utcnow()))) + "." + file_type
    file.save(filepath)
    return jsonify({"status": 1, "src": src})
