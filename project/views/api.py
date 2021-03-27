from flask import Blueprint, render_template, request, session, jsonify, redirect

from ..database import *
from ..models import *

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/post/add", methods=["POST"])
def create_post():
    Bid = request.form.get("Bid")
    if not Bid or not Bid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 404
    data = {"Bid": Bid}
    Uid = session.get("Uid")
    if not Uid:
        return render_template("create.html", data=data, error="Not logged in!")
    match_board = db_session.query(Board).filter(Board.Bid == Bid).all()
    if not match_board:
        return jsonify({"error": {"msg": "invalid board ID"}}), 404
    title = request.form.get("title")
    content = request.form.get("content")
    new_post = Post(Uid, Bid, title, content)
    DB_session.add(new_post)
    DB_session.commit()
    return redirect("/board/" + Bid)