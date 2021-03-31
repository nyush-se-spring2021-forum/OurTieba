from contextlib import contextmanager
import functools

from flask import session, redirect


def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("Uid"):
            return f(*args, **kwargs)
        else:
            return redirect("/login")

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
