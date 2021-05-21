import logging

from .database import *  # must import this line here, otherwise cannot get sqlalchemy's logger


class Logger:
    def __init__(self, env="development"):
        self.engine = my_db.get_engine().name
        filename = "test.log" if env == "development" else "OutTieba.log"
        logging.basicConfig(filename=f"ourtieba/logs/{filename}",
                            level=logging.DEBUG,
                            format='%(asctime)s [%(thread)d:%(threadName)s] [%(filename)s:%(module)s:%(funcName)s] '
                                   '[%(levelname)s]: %(message)s',
                            filemode='a',
                            datefmt='%Y-%m-%d %A %H:%M:%S'
                            )
        self.logger = logging.getLogger('sqlalchemy.engine')
        self.logger.setLevel(logging.INFO)
        logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)


def init_logger(*args, **kwargs):
    logger = Logger(*args, **kwargs)
    return logger
