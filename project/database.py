from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from .configs.functions import *

engine = create_engine('sqlite:///test.db', convert_unicode=True)
DB_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = DB_session.query_property()


class myDb:
    __instance = None

    # ensure only one instance is created
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self._session = None

    def connect(self, *args, **kwargs):
        self._session = DB_session  # must use scoped session here

    def query(self, target, condition=True, order=True, first=False):
        with auto_scope(self._session) as _db_session:
            if first:
                return _db_session.query(target).filter(condition).order_by(order).first()
            return _db_session.query(target).filter(condition).order_by(order).all()  # can be None

    def add(self, new):
        with auto_scope(self._session) as _db_session:
            _db_session.add(new)

    def merge(self, new):
        with auto_scope(self._session) as _db_session:
            _db_session.merge(new)

    def delete(self, target, condition=False, synchronize_session=True):
        with auto_scope(self._session) as _db_session:
            affected_rows = _db_session.query(target).filter(condition).delete(synchronize_session)
            return affected_rows

    def avg(self, target, condition=True):
        with auto_scope(self._session) as _db_session:
            return _db_session.query(func.avg(target)).filter(condition).scalar()

    def count(self, target, condition=True):
        with auto_scope(self._session) as _db_session:
            return _db_session.query(func.count(target)).filter(condition).scalar()

    def close(self):
        self._session.remove()


my_db = myDb()


def init_db():
    # import all models here (only the class name)
    from .models import Admin, Board, Comment, CommentStatus, Post, PostStatus, Report, User
    Base.metadata.create_all(bind=engine)
    my_db.connect()
