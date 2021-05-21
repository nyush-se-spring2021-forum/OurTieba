import logging

from .database import *  # must import this line here, otherwise cannot get sqlalchemy's logger


class Logger:
    """
    Logger class used to record logs during runtime.
    """
    def __init__(self, lg_path):
        logging.basicConfig(filename=lg_path,
                            level=logging.DEBUG,
                            format='%(asctime)s [%(thread)d:%(threadName)s] [%(filename)s:%(module)s:%(funcName)s] '
                                   '[%(levelname)s]: %(message)s',
                            filemode='a',
                            datefmt='%Y-%m-%d %A %H:%M:%S'
                            )
        self.logger = logging.getLogger('sqlalchemy.engine')
        self.logger.setLevel(logging.INFO)
        logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)


def init_logger(app):
    """
    Initialize logger for Flask app.
    :param app: Flask app instance.
    :return: logger instance.
    """
    lg_path = app.config['LOGGER_PATH']
    logger = Logger(lg_path=lg_path)
    return logger
