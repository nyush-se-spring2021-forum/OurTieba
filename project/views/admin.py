import datetime

from flask import Blueprint, render_template, request, session, jsonify, redirect
import hashlib

from ..database import *
from ..models import *

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/")
def admin_hello():
    return redirect("/admin/dashboard")


@admin.route("/login")
def admin_login():
    return render_template("admin_login.html")


@admin.route("/dashboard")
def admin_dashboard():
    page = request.args.get("page", "1")
    order = Report.timestamp.desc()
    Aid = session.get("Aid")
    type = session.get("type")
    if type != "admin":
        return "Invalid URL", 404
    match_admin = db_session(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return "Invalid URL", 404

    reports = db_session.query(Report).filter(Report.resolved == 0).order_by(order).all()
    num_reports = len(reports)
    num_page = (num_reports - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    Allreports = [{"Rid": r.Rid, "target": r.target, "target_ID": r.targetId, "reason": r.reason,
                   "timestamp": r.timestamp, "Uid": r.Uid}
                  for r in reports[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]]
    data = {"num_match": num_reports, "num_page": num_page, "page": page, "reports": Allreports}
    db_session.commit()
    return render_template("admin_dashboard.html", data=data)


@admin.route("/auth/login", methods=["POST"])
def admin_auth_login():
    aname = request.form.get("aname")
    password = request.form.get("password")

    admin_result = db_session.query(Admin).filter(Admin.aname == aname).first()
    if len(admin_result) == 0:
        return jsonify({"error": {"msg": "aname Not Found"}}, 403)
    encoded_password = hashlib.sha3_512(password.encode()).hexdigest()
    recorded_password = admin_result.password
    if encoded_password != recorded_password:
        return jsonify({"error": {"msg": "Incorrect Password"}}, 403)

    db_session.commit()
    session["Aid"] = admin_result.Aid
    session["type"] = "admin"
    return redirect("/dashboard")


@admin.route("/board/delete", methods=["POST"])
def admin_board_delete():
    Aid = session.get("Aid")
    type = session.get("type")
    if type != "admin":
        return "Invalid URL", 404
    match_admin = db_session(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return "Invalid URL", 404

    Bid = request.form.get("Bid")
    match_board = db_session(Board).filter(Board.Bid == Bid).all()
    if len(match_board) == 0:
        return jsonify({"error": {"msg": "Bid not Found"}}, 403)
    db_session.delete(match_board)
    db_session.commit()
    return redirect("/dashboard")


@admin.route("/post/delete", methods=["POST"])
def admin_post_delete():
    Aid = session.get("Aid")
    type = session.get("type")
    if type != "admin":
        return "Invalid URL", 404
    match_admin = db_session(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return "Invalid URL", 404

    Pid = request.form.get("Pid")
    match_post = db_session(Post).filter(Post.Pid == Pid).all()
    if len(match_post) == 0:
        return jsonify({"error": {"msg": "Pid not Found"}}, 403)
    db_session.delete(match_post)
    db_session.commit()
    return redirect("/dashboard")


@admin.route("/comment/delete", methods=["POST"])
def admin_comment_delete():
    Aid = session.get("Aid")
    type = session.get("type")
    if type != "admin":
        return "Invalid URL", 404
    match_admin = db_session(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return "Invalid URL", 404

    Cid = request.form.get("Cid")
    match_comment = db_session(Comment).filter(Comment.Cid == Cid).all()
    if len(match_comment) == 0:
        return jsonify({"error": {"msg": "Cid not Found"}}, 403)
    db_session.delete(match_comment)
    db_session.commit()
    return redirect("/dashboard")


@admin.route("/user/ban", methods=["POST"])
def admin_user_ban():
    Aid = session.get("Aid")
    type = session.get("type")
    if type != "admin":
        return "Invalid URL", 404
    match_admin = db_session(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return "Invalid URL", 404

    Uid = request.form.get("Uid")
    days = request.form.get("days")
    match_user = db_session(User).filter(User.Uid == Uid).first()
    if len(match_user) == 0:
        return jsonify({"error": {"msg": "Uid not Found"}}, 403)
    if not days.isnumeric() or int(days) <= 0:
        return jsonify({"error": {"msg": "Invalid Day"}}, 403)
    match_user.banned = 1
    match_user.banDuration = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    db_session.commit()
    return redirect("/dashboard")


@admin.route("/user/unban", methods=["POST"])
def admin_user_unban():
    Aid = session.get("Aid")
    type = session.get("type")
    if type != "admin":
        return "Invalid URL", 404
    match_admin = db_session(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return "Invalid URL", 404

    Uid = request.form.get("Uid")
    match_user = db_session(User).filter(User.Uid == Uid).first()
    if len(match_user) == 0:
        return jsonify({"error": {"msg": "Uid not Found"}}, 403)
    user.banned = 0
    db_session.commit()
    return redirect("/dashboard")


@admin.route("/report/resolve", methods=["POST"])
def admin_report_resolve():
    Aid = session.get("Aid")
    type = session.get("type")
    if type != "admin":
        return "Invalid URL", 404
    match_admin = db_session(Admin).filter(Admin.Aid == Aid).all()
    if len(match_admin) == 0:
        return "Invalid URL", 404

    Rid = request.form.get("Rid")
    match_report = db_session(Report).filter(Report.Rid == Rid).first()
    if len(match_report) == 0:
        return jsonify({"error": {"msg": "Rid not Found"}}, 403)
    match_report.resolved = 1
    db_session.commit()
    return redirect("/dashboard")
