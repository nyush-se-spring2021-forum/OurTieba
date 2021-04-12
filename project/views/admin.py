import datetime
import hashlib

from flask import Blueprint, jsonify, render_template, request

from ..configs import *
from ..database import *
from ..models import *

admin_blue = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blue.route("/")
def admin_hello():
    return redirect("/admin/dashboard")


@admin_blue.route("/login")
def admin_login():
    return render_template("admin_login.html")


@admin_blue.route("/dashboard")
@admin_login_required
def admin_dashboard():
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
    aname = request.form.get("aname")
    password = request.form.get("password")

    admin_result = my_db.query(Admin, Admin.aname == aname, first=True)
    if not admin_result:
        return jsonify({"error": {"msg": "aname Not Found"}}, 403)
    encoded_password = hashlib.sha3_512(password.encode()).hexdigest()
    recorded_password = admin_result.password
    if encoded_password != recorded_password:
        return jsonify({"error": {"msg": "Incorrect Password"}}, 403)

    session["Aid"] = admin_result.Aid
    admin_info = {"nickname": admin_result.nickname, "avatar": admin_result.avatar}
    session["admin_info"] = admin_info

    return redirect("/admin/dashboard")


@admin_blue.route("/auth/logout")
@admin_login_required
def admin_logout():
    session.clear()
    return redirect("/admin/auth/login")


@admin_blue.route("/board/delete", methods=["POST"])
@admin_login_required
def admin_board_delete():
    Bid = request.form.get("Bid")
    match_board = my_db.delete(Board, Board.Bid == Bid)
    if len(match_board) == 0:
        return jsonify({"error": {"msg": "Bid not Found"}}, 403)
    return redirect("/admin/dashboard")


@admin_blue.route("/post/delete", methods=["POST"])
@admin_login_required
def admin_post_delete():
    Pid = request.form.get("Pid")
    match_post = my_db.delete(Post, Post.Pid == Pid)
    if not match_post:
        return jsonify({"error": {"msg": "Pid not Found"}}, 403)
    match_post.under.postCount -= 1
    return redirect("/admin/dashboard")


@admin_blue.route("/comment/delete", methods=["POST"])
@admin_login_required
def admin_comment_delete():
    Cid = request.form.get("Cid")
    match_comment = my_db.delete(Comment, Comment.Cid == Cid)
    if not match_comment:
        return jsonify({"error": {"msg": "Cid not Found"}}, 403)
    match_comment.comment_in.commentCount -= 1
    return redirect("/admin/dashboard")


@admin_blue.route("/user/ban", methods=["POST"])
@admin_login_required
def admin_user_ban():
    Uid = request.form.get("Uid")
    days = request.form.get("days")
    match_user = my_db.query(User, User.Uid == Uid, first=True)
    if len(match_user) == 0:
        return jsonify({"error": {"msg": "Uid not Found"}}, 403)
    if not days.isnumeric() or int(days) <= 0:
        return jsonify({"error": {"msg": "Invalid Day"}}, 403)
    match_user.banned = 1
    match_user.banDuration = datetime.datetime.now() + datetime.timedelta(days=days)
    return redirect("/admin/dashboard")


@admin_blue.route("/user/unban", methods=["POST"])
@admin_login_required
def admin_user_unban():
    Uid = request.form.get("Uid")
    match_user = my_db.query(User, User.Uid == Uid, first=True)
    if len(match_user) == 0:
        return jsonify({"error": {"msg": "Uid not Found"}}, 403)
    user.banned = 0
    return redirect("/admin/dashboard")


@admin_blue.route("/report/resolve", methods=["POST"])
@admin_login_required
def admin_report_resolve():
    Rid = request.form.get("Rid")
    match_report = my_db.query(Report, Report.Rid == Rid, first=True)
    if not match_report:
        return jsonify({"error": {"msg": "Rid not Found"}}, 403)
    match_report.resolved = 1
    return redirect("/admin/dashboard")
