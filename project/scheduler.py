from flask_apscheduler import APScheduler

from .logger import *
from .models import *

# logger = init_logger()


def update_hot():
    """ Not Finished!"""
    print("updating hot...")
    # logger.logger.info("Start updating hot")
    print("average hot:", db_session.query(func.avg(Board.hot).label("average")).scalar())
    db_session.commit()


def init_scheduler(app):
    scheduler = APScheduler()
    scheduler.add_job(func=update_hot, id="1", trigger="interval", seconds=86400)  # trigger everyday
    scheduler.init_app(app)
    scheduler.start()
