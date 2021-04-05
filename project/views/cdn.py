from flask import Blueprint, send_file


cdn = Blueprint("cdn", __name__, url_prefix="/cdn")


@cdn.route("/<filename>")
def cdn_send_file(filename):
    return send_file(f"../cdn/{filename}")