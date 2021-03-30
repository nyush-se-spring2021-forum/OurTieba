from contextlib import contextmanager

from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('sqlite:///test.db', convert_unicode=True)
DB_session = scoped_session(sessionmaker(bind=engine))

db_session = DB_session()

Base = declarative_base()
Base.query = DB_session.query_property()


def init_db():
    # import all models here (only the class name)
    from .models import Admin, Board, Comment, CommentStatus, Post, PostStatus, Report, User
    Base.metadata.create_all(bind=engine)


@contextmanager
def auto_scope(session):
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)


class myDb:
    def __init__(self):
        self._session = DB_session  # must use scoped session here

    def query(self, target, condition=True, order=True, first=False):
        with auto_scope(self._session) as _db_session:
            if first:
                return _db_session.query(target).filter(condition).order_by(order).first()
            return _db_session.query(target).filter(condition).order_by(order).all()  # can be None

    def add(self, new):
        with auto_scope(self._session) as _db_session:
            _db_session.add(new)

    def delete(self, target, condition=False, synchronize_session=True):
        with auto_scope(self._session) as _db_session:
            affected_rows = _db_session.query(target).filter(condition).delete(synchronize_session)
            return affected_rows

    def avg(self, target):
        with auto_scope(self._session) as _db_session:
            return _db_session.query(func.avg(target)).scalar()

    def count(self, target):
        with auto_scope(self._session) as _db_session:
            return _db_session.query(func.count(target)).scalar()

    def close(self):
        self._session.remove()
