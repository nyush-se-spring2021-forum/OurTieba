import functools

from flask import session, redirect


# Macros
PAGE_SIZE = 10
RECOMMEND_NUM_BOARD = 10
RECOMMEND_NUM_NEWS = 3


def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("Uid"):
            return f(*args, **kwargs)
        else:
            return redirect("/login")

    return wrapper