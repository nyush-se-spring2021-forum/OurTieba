from sqlalchemy import create_engine, func, inspect, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from .configs import auto_scope


class myDb:
    __instance = None

    Base = declarative_base()

    # ensure that only one instance is created
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self._engine = None
        self._session = None

    def connect(self, *args, **kwargs):
        self._engine = create_engine('sqlite:///test.db', convert_unicode=True)
        # must use scoped session here
        self._session = scoped_session(sessionmaker(self._engine, *args, **kwargs))
        self.Base.query = self._session.query_property()

    def initialize(self, *args, **kwargs):
        self.connect(*args, **kwargs)
        # import all models here (only the class name)
        from .models import Admin, Board, Comment, CommentStatus, Post, PostStatus, Report, Subscription,\
            User, user_report_table
        self.Base.metadata.create_all(bind=self._engine)

    def query(self, target, condition=True, order=True, first=False):
        with auto_scope(self._session) as _db_session:
            if first:
                return _db_session.query(target).filter(condition).order_by(order).first()
            return _db_session.query(target).filter(condition).order_by(order).all() or []  # if None return []

    def query_join(self, target, join, condition=True, order=True, first=False, count=False):
        with auto_scope(self._session) as _db_session:
            if first:
                return _db_session.query(target).join(join).filter(condition).order_by(order).first()
            if count:
                return _db_session.query(func.count(target)).join(join).filter(condition).order_by(order).scalar()
            return _db_session.query(target).join(join).filter(condition).order_by(order).all() or []

    def add(self, new):
        with auto_scope(self._session) as _db_session:
            return _db_session.add(new)

    def merge(self, new):
        with auto_scope(self._session) as _db_session:
            return _db_session.merge(new)

    def delete(self, target, condition=False, synchronize_session="fetch"):
        with auto_scope(self._session) as _db_session:
            return _db_session.query(target).filter(condition).delete(synchronize_session)

    def avg(self, target, condition=True):
        with auto_scope(self._session) as _db_session:
            return _db_session.query(func.avg(target)).filter(condition).scalar()

    def count(self, target, condition=True):
        if issubclass(target, self.Base):
            target = inspect(target).primary_key[0]
        with auto_scope(self._session) as _db_session:
            return _db_session.query(func.count(target)).filter(condition).scalar()

    def update(self, target, condition=True, **kwargs):
        with auto_scope(self._session) as _db_session:
            values = kwargs.get("values")  # "values" is a dict
            if values:
                return _db_session.query(target).filter(condition).update(values)

    def close(self):
        self._session.remove()

    def get_engine(self):
        return self._engine

    def set_engine(self, _new_engine):
        self._engine = _new_engine


class dbFactory:
    @staticmethod
    def produce():
        return myDb()


my_db = dbFactory.produce()


def init_db():
    my_db.initialize()
