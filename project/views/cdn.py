from flask import Blueprint, make_response, send_file


cdn = Blueprint("cdn", __name__, url_prefix="/cdn")


@cdn.route("/<filename>")
def cdn_send_file(filename):
    res = make_response(send_file(f"../cdn/{filename}"))
    res.headers["Cache-Control"] = "public, max-age=86400"
    res.headers.pop("Expires")
    return res