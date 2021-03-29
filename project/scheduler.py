from flask_apscheduler import APScheduler

from .database import *
from .models import *


def update_hot():
    print("updating hot...")
    print("average hot:", db_session.query(func.avg(Board.hot).label("average")).scalar())
    db_session.commit()


def init_scheduler(app):
    scheduler = APScheduler()
    scheduler.add_job(func=update_hot, id="1", trigger="interval", seconds=86400)  # trigger everyday
    scheduler.init_app(app)
    scheduler.start()
