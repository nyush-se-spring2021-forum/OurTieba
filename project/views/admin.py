import hashlib

from flask import Blueprint, jsonify, render_template, request

from ..configs import *
from ..database import *
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

    match_reports = my_db.query(Report, Report.resolved == 0, order)
    num_reports = len(match_reports)
    num_page = (num_reports - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    reports = [{"Rid": r.Rid, "target": r.target, "target_ID": r.targetId, "reason": r.reason,
                "timestamp": r.timestamp, "Uid": r.Uid}
               for r in match_reports[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]]
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
        return jsonify({"error": {"msg": "Invalid input."}, "status": 0})

    admin_result = my_db.query(Admin, Admin.aname == aname, first=True)
    if not admin_result:
        return jsonify({"error": {"msg": "Admin name Not Found"}, 'status': 0})
    encoded_password = hashlib.sha3_512(password.encode()).hexdigest()
    recorded_password = admin_result.password
    if encoded_password != recorded_password:
        return jsonify({"error": {"msg": "Incorrect Password"}, 'status': 0})

    session["Aid"] = admin_result.Aid
    admin_info = {"nickname": admin_result.nickname, "avatar": admin_result.avatar}
    session["admin_info"] = admin_info
    # session.permanent = True
    return jsonify({'status': 1})


@admin_blue.route("/auth/logout")
@admin_login_required
def admin_logout():
    """
    This function is used for logged in admins to logout
    :return: redirect to another path of '/admin/login'
    """
    session.clear()
    return redirect("/admin/login")


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
        return jsonify({"error": {"msg": "invalid data"}, "status": 0})
    affected_row = my_db.delete(Board, Board.Bid == Bid)
    if not affected_row:
        return jsonify({"error": {"msg": "Bid not Found"}, "status": 0})
    #Then delete all corresponding posts and comments in that Bid
    match_posts = my_db.query(Post, Post.Bid == Bid)
    for i in match_posts:
        match_comments = my_db.query(Comment, Comment.Pid == i.Pid)
        for j in match_comments:
            media_list = j.medias
            cd = os.getcwd()
            for f in media_list:
                while True:
                    try:
                        os.remove(cd + "/cdn/" + f)
                        break
                    except:
                        continue
            my_db.delete(Comment, Comment.Cid == j.Cid)
            my_db.delete(CommentStatus, CommentStatus.Cid == j.Cid)
        media_list = i.medias
        cd = os.getcwd()
        for f in media_list:
            while True:
                try:
                    os.remove(cd + "/cdn/" + f)
                    break
                except:
                    continue
        my_db.delete(Post, Post.Pid == i.Pid)
        my_db.delete(PostStatus, PostStatus.Pid == i.Pid)
        my_db.delete(History, History.Pid == i.Pid)
    return jsonify({'status': 1})


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
        return jsonify({"error": {"msg": "invalid data"}, "status": 0})
    match_post = my_db.query(Post, Post.Pid == Pid, first=True)
    if not match_post:
        return jsonify({"error": {"msg": "Pid not Found"}, "status": 0})

    media_list = match_post.medias
    cd = os.getcwd()
    for i in media_list:
        while True:
            try:
                os.remove(cd + "/cdn/" + i)
                break
            except:
                continue

    match_post.under.postCount -= 1
    my_db.delete(Post, Post.Pid == Pid)
    # Then delete all corresponding data in other relating tables
    result = my_db.query(Comment, Comment.Pid == Pid)
    for i in result:
        my_db.delete(CommentStatus, CommentStatus.Cid == i.Cid)
        my_db.delete(Comment, Comment.Pid == Pid)
        media_list = i.medias
        cd = os.getcwd()
        for f in media_list:
            while True:
                try:
                    os.remove(cd + "/cdn/" + f)
                    break
                except:
                    continue
    my_db.delete(PostStatus, PostStatus.Pid == Pid)
    my_db.delete(History, History.Pid == Pid)
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
        return jsonify({"error": {"msg": "invalid data"}, "status": 0})
    match_comment = my_db.query(Comment, Comment.Cid == Cid, first=True)
    if not match_comment:
        return jsonify({"error": {"msg": "Cid not Found"}, "status": 0})

    media_list = match_comment.medias
    cd = os.getcwd()
    for i in media_list:
        while True:
            try:
                os.remove(cd + "/cdn/" + i)
                break
            except:
                continue


    match_comment.comment_in.commentCount -= 1
    my_db.delete(Comment, Comment.Cid == Cid)
    my_db.delete(CommentStatus, CommentStatus.Cid == Cid)
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
        return jsonify({"error": {"msg": "Invalid data"}, "status": 0})
    affected_row = my_db.update(User, User.Uid == Uid, values={"banned": 1,
                                "banDuration": datetime.datetime.utcnow() + datetime.timedelta(days=int(days))})
    if not affected_row:
        return jsonify({"error": {"msg": "Uid not Found"}, "status": 0})
    return jsonify({'status': 1})


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
        return jsonify({"error": {"msg": "Invalid data"}, "status": 0})
    affected_row = my_db.update(User, User.Uid == Uid, values={"banned": 0})
    if not affected_row:
        return jsonify({"error": {"msg": "Uid not Found"}, "status": 0})
    return jsonify({'status': 1})


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
        return jsonify({"error": {"msg": "invalid data"}, "status": 0})
    affected_row = my_db.update(Report, Report.Rid == Rid, values={"resolved": 1})
    if not affected_row:
        return jsonify({"error": {"msg": "Rid not Found"}, "status": 0})
    return jsonify({'status': 1})
