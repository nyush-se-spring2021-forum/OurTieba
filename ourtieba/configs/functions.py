import datetime
import functools
from contextlib import contextmanager

from flask import session, redirect


# For now, we just assume that all the sessions are not tampered.
# Forgery may be possible, but it's csrf token's lob to find it out
# (which we haven't implemented yet).
def login_required(f):
    """
    Decorator of view (controller) functions to check whether user is logged in or not. If not, will not execute view
    function but redirect user to login page.
    :param f: view function object.
    :return: decorated view function object.
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("Uid"):
            return f(*args, **kwargs)
        else:
            return redirect("/login")

    return wrapper


def admin_login_required(f):
    """
    Similar to func login_required. The target is admin not user.
    :param f: view function object.
    :return: decorated view function object.
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("Aid"):
            return f(*args, **kwargs)
        else:
            return redirect("/admin/login")

    return wrapper


@contextmanager
def auto_scope(_session):
    """
    Generator of self-designed database session that does not throw exceptions but print them (in log, because stdout is
    implicitly set to logger file). Also, auto-commit and auto-rollback is achieved.
    :param _session: SQLAlchemy database session
    :return: scoped session
    """
    if not _session:
        raise Exception("Please connect to database first!")
    try:
        yield _session
        _session.commit()
    except Exception as e:
        _session.rollback()
        print(e)


def convert_time(ts: datetime.datetime):
    """
    Convert datetime object into beautified string that is easy to read on web page. If on the same day, will return
    "Today" + "hour:minutes"; if in the same year, will return "month-days"; else will return "year-month-days".
    :param ts: timestamp (not the UNIX one, but datetime object).
    :return: time string.
    """
    if ts.strftime("%Y") != datetime.datetime.utcnow().strftime("%Y"):
        return ts.strftime("%Y-%m-%d")
    if (day := ts.strftime("%m-%d")) != datetime.datetime.utcnow().strftime("%m-%d"):
        return day
    return "Today " + ts.strftime("%H:%M")


if __name__ == '__main__':
    new = datetime.datetime(2021, 5, 9, 15, 0, 0)
    print(convert_time(new))
