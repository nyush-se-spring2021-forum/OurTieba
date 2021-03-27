from flask import Blueprint, render_template, request, session, jsonify

from ..database import *
from ..models import *

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/create_post", methods=["POST"])
def create_post():
    Bid = request.form.get("Bid")
    if not Bid or not Bid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 404
    Uid = session.get("Uid")
    if not Uid:
        return render_template("create.html", Bid=Bid, error="Not logged in!")
    match_board = db_session.query(Board).filter(Board.Bid == Bid).all()
    if not match_board:
        return jsonify({"error": {"msg": "invalid board ID"}}), 404
    return render_template("index.html")