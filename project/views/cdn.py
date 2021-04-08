from flask import Blueprint, make_response, abort, send_from_directory

from ..configs import *


cdn = Blueprint("cdn", __name__, url_prefix="/cdn")


@cdn.route("/<filename>")
def cdn_send_file(filename):
    # check whether file exists
    if not os.path.isfile(CDN_PATH + filename):
        abort(404)
    res = make_response(send_from_directory(CDN_PATH, filename))
    res.headers["Cache-Control"] = "public, max-age=86400"
    res.headers.pop("Expires")
    return res