import logging

from .database import *  # must import this line here, otherwise cannot get sqlalchemy's logger


class Logger:
    def __init__(self):
        self.engine = engine.name
        logging.basicConfig(filename="project/logs/test.log",
                            level=logging.DEBUG,
                            format='%(asctime)s [%(thread)d:%(threadName)s] [%(filename)s:%(module)s:%(funcName)s] '
                                   '[%(levelname)s]: %(message)s',
                            filemode='a',
                            datefmt='%Y-%m-%d %A %H:%M:%S'
                            )
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def init_logger():
    logger = Logger()
    return logger
