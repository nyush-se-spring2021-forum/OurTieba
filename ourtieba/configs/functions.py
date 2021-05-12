from contextlib import contextmanager
import datetime
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


def convert_time(ts: datetime.datetime):
    if ts.strftime("%Y") != datetime.datetime.utcnow().strftime("%Y"):
        return ts.strftime("%Y-%m-%d")
    if (day := ts.strftime("%m-%d")) != datetime.datetime.utcnow().strftime("%m-%d"):
        return day
    return "Today " + ts.strftime("%H:%M")


if __name__ == '__main__':
    new = datetime.datetime(2021, 5, 9, 15, 0, 0)
    print(convert_time(new))