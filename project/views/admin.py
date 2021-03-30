import datetime
import hashlib

from flask import Blueprint, render_template, request, session, jsonify, redirect

from ..configs.macros import *
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
def admin_dashboard():
    page = request.args.get("page", "1")
    order = Report.timestamp.desc()
    Aid = session.get("Aid")

    match_admin = my_db.query(Admin, Admin.Aid == Aid)
    #match_admin = db_session.query(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return redirect("/admin/login")

    match_reports = my_db.query(Report, Report.resolved == 0, order)
    #match_reports = db_session.query(Report).filter(Report.resolved == 0).order_by(order).all()
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
    #admin_result = db_session.query(Admin).filter(Admin.aname == aname).first()
    if len(admin_result) == 0:
        return jsonify({"error": {"msg": "aname Not Found"}}, 403)
    encoded_password = hashlib.sha3_512(password.encode()).hexdigest()
    recorded_password = admin_result.password
    if encoded_password != recorded_password:
        return jsonify({"error": {"msg": "Incorrect Password"}}, 403)

    session["Aid"] = admin_result.Aid

    return redirect("/admin/dashboard")


@admin_blue.route("/auth/logout")
def admin_logout():
    Aid = session.get("Aid")
    if not Aid:
        return redirect("/admin/login")
    session.pop("Aid")  # may raise KeyError, must check before pop

    return redirect("/admin/auth/login")


@admin_blue.route("/board/delete", methods=["POST"])
def admin_board_delete():
    Aid = session.get("Aid")

    match_admin = my_db.query(Admin, Admin.Aid == Aid)
    #match_admin = db_session.query(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return redirect("/admin/login")

    Bid = request.form.get("Bid")
    match_board = my_db.delete(Board, Board.Bid == Bid)
    #match_board = db_session.query(Board).filter(Board.Bid == Bid).all()
    if len(match_board) == 0:
        return jsonify({"error": {"msg": "Bid not Found"}}, 403)
    #db_session.delete(match_board)
    return redirect("/admin/dashboard")


@admin_blue.route("/post/delete", methods=["POST"])
def admin_post_delete():
    Aid = session.get("Aid")

    match_admin = my_db.query(Admin, Admin.Aid == Aid)
    #match_admin = db_session.query(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return redirect("/admin/login")

    Pid = request.form.get("Pid")
    match_post = my_db.delete(Post, Post.Pid == Pid, first=True)
    #match_post = db_session.query(Post).filter(Post.Pid == Pid).first()
    if not match_post:
        return jsonify({"error": {"msg": "Pid not Found"}}, 403)
    match_post.under.postCount -= 1
    #db_session.delete(match_post)
    return redirect("/admin/dashboard")


@admin_blue.route("/comment/delete", methods=["POST"])
def admin_comment_delete():
    Aid = session.get("Aid")

    match_admin = my_db.query(Admin, Admin.Aid == Aid)
    #match_admin = db_session.query(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return redirect("/admin/login")

    Cid = request.form.get("Cid")
    match_comment = my_db.delete(Comment, Comment.Cid == Cid, first=True)
    #match_comment = db_session.query(Comment).filter(Comment.Cid == Cid).first()
    if not match_comment:
        return jsonify({"error": {"msg": "Cid not Found"}}, 403)
    match_comment.comment_in.commentCount -= 1
    #db_session.delete(match_comment)
    return redirect("/admin/dashboard")


@admin_blue.route("/user/ban", methods=["POST"])
def admin_user_ban():
    Aid = session.get("Aid")

    match_admin = my_db.query(Admin, Admin.Aid == Aid)
    #match_admin = db_session.query(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return redirect("/admin/login")

    Uid = request.form.get("Uid")
    days = request.form.get("days")
    match_user = my_db.query(User, User.Uid == Uid, first=True)
    #match_user = db_session.query(User).filter(User.Uid == Uid).first()
    if len(match_user) == 0:
        return jsonify({"error": {"msg": "Uid not Found"}}, 403)
    if not days.isnumeric() or int(days) <= 0:
        return jsonify({"error": {"msg": "Invalid Day"}}, 403)
    match_user.banned = 1
    match_user.banDuration = datetime.datetime.now() + datetime.timedelta(days=days)
    return redirect("/admin/dashboard")


@admin_blue.route("/user/unban", methods=["POST"])
def admin_user_unban():
    Aid = session.get("Aid")

    match_admin = my_db.query(Admin, Admin.Aid == Aid)
    #match_admin = db_session.query(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return redirect("/admin/login")

    Uid = request.form.get("Uid")
    match_user = my_db.query(User, User.Uid == Uid, first=True)
    #match_user = db_session.query(User).filter(User.Uid == Uid).first()
    if len(match_user) == 0:
        return jsonify({"error": {"msg": "Uid not Found"}}, 403)
    user.banned = 0
    return redirect("/admin/dashboard")


@admin_blue.route("/report/resolve", methods=["POST"])
def admin_report_resolve():
    Aid = session.get("Aid")

    match_admin = my_db.query(Admin, Admin.Aid == Aid)
    #match_admin = db_session.query(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return redirect("/admin/login")

    Rid = request.form.get("Rid")
    match_report = my_db.query(Report, Report.Rid == Rid, first=True)
    #match_report = db_session.query(Report).filter(Report.Rid == Rid).first()
    if len(match_report) == 0:
        return jsonify({"error": {"msg": "Rid not Found"}}, 403)
    match_report.resolved = 1
    return redirect("/admin/dashboard")
