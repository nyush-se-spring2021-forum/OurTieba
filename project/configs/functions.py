from contextlib import contextmanager
import functools

from flask import session, redirect


# For now, we just assume that all the sessions are not tampered.
# Forgery may be possible, but it's csrf token's lob to find it out
# (which we haven't implemented yet).
def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("Uid"):
            return f(*args, **kwargs)
        else:
            return redirect("/login")

    return wrapper


def admin_login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("Aid"):
            return f(*args, **kwargs)
        else:
            return redirect("/admin/login")

    return wrapper


@contextmanager
def auto_scope(_session):
    if not _session:
        raise Exception("Please connect to database first!")
    try:
        yield _session
        _session.commit()
    except Exception as e:
        _session.rollback()
        print(e)
