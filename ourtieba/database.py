from sqlalchemy import create_engine, func, inspect, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from .configs import auto_scope


class myDb:
    """
    Database class used for querying from, inserting into, merging into, updating and deleting from database.
    """
    __instance = None

    Base = declarative_base()

    # ensure that only one instance is created (singleton design)
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self._engine = None
        self._session = None

    def connect(self, *args, db_path, **kwargs):
        """
        Connect to database. Database engine will be created and bind to database session.
        :param args: positional arguments.
        :param db_path: database path.
        :param kwargs: keyword arguments.
        :return: None.
        """
        self._engine = create_engine(db_path, convert_unicode=True)
        # must use scoped session here
        self._session = scoped_session(sessionmaker(self._engine, *args, **kwargs))
        self.Base.query = self._session.query_property()

    def initialize(self, *args, **kwargs):
        """
        Connect to database and create all tables if not exist.
        :param args: positional arguments.
        :param kwargs: keyword arguments.
        :return: None.
        """
        self.connect(*args, **kwargs)
        # import all models here (only the class name)
        from .models import Admin, Board, Comment, CommentStatus, History, Post, PostStatus, Report, Subscription,\
            User, user_report_table
        self.Base.metadata.create_all(bind=self._engine)

    def query(self, target, condition=True, order=True, first=False, limit=False, offset=0):
        """
        Encapsulate sqlalchemy's database session (after auto scoping)'s query method. Get instance(s) by conditions.
        Only one of the "first" and "limit" parameters will be valid.
        :param target: table/column to query from.
        :param condition: filtering conditions.
        :param order: the order to query by.
        :param first: whether to fetch the first match or not.
        :param limit: how many result to fetch.
        :param offset: from where to fetch.
        :return: list of matched instances (rows) or a single matched instance or [].
        """
        with auto_scope(self._session) as _db_session:
            if first:
                return _db_session.query(target).filter(condition).order_by(order).first()
            if limit:
                return _db_session.query(target).filter(condition).order_by(order).limit(limit).offset(offset).all() \
                       or []
            return _db_session.query(target).filter(condition).order_by(order).all() or []  # if None return []

    def query_join(self, target, join, condition=True, order=True, first=False, count=False):
        """
        Encapsulate sqlalchemy's database session (after auto scoping)'s query method with join enabled. Get instance(s)
        by conditions.
        :param target: table/column to query from.
        :param join: the table to join.
        :param condition: filtering conditions.
        :param order: the order to query by.
        :param first: whether to fetch the first match or not.
        :param count: whether return count or not
        :return: list of matched instances or a single matched instance or count of matched instance(s) or [].
        """
        with auto_scope(self._session) as _db_session:
            if first:
                return _db_session.query(target).join(join).filter(condition).order_by(order).first()
            if count:
                if issubclass(target, self.Base):
                    target = inspect(target).primary_key[0]
                return _db_session.query(func.count(target)).join(join).filter(condition).order_by(order).scalar()
            return _db_session.query(target).join(join).filter(condition).order_by(order).all() or []

    def get(self, target, primary_key):
        """
        Encapsulate sqlalchemy's database session (after auto scoping)'s get method. Get an instance by primary key.
        :param target: table/column to get from.
        :param primary_key: primary key to query for.
        :return: a single matched instance or None.
        """
        with auto_scope(self._session) as _db_session:
            return _db_session.query(target).get(primary_key)

    def add(self, new):
        """
        Encapsulate sqlalchemy's database session (after auto scoping)'s add method. Add a new instance to database.
        :param new: the new instance to add.
        :return: 0 (failure) or 1 (success).
        """
        with auto_scope(self._session) as _db_session:
            return _db_session.add(new)

    def merge(self, new):
        """
        Encapsulate sqlalchemy's database session (after auto scoping)'s merge method. Merge an instance to database.
        :param new: the instance to merge.
        :return: 0 (failure) or 1 (success).
        """
        with auto_scope(self._session) as _db_session:
            return _db_session.merge(new)

    def delete(self, target, condition=False, synchronize_session="fetch"):
        """
        Encapsulate sqlalchemy's database session (after auto scoping)'s merge method. Merge an instance to database.
        :param target: table/column to delete from.
        :param condition: filtering conditions.
        :param synchronize_session: the way to synchronize session before deletion.
        :return: 0 (failure) or 1 (success).
        """
        with auto_scope(self._session) as _db_session:
            return _db_session.query(target).filter(condition).delete(synchronize_session)

    def avg(self, target, condition=True):
        """
        Encapsulate sqlalchemy's database session (after auto scoping)'s query method using func avg. Get the average of
        certain columns of instances.
        :param target: table/column to compute average with.
        :param condition: filtering conditions.
        :return: the average.
        """
        with auto_scope(self._session) as _db_session:
            return _db_session.query(func.avg(target)).filter(condition).scalar()

    def count(self, target, condition=True):
        """
        Encapsulate sqlalchemy's database session (after auto scoping)'s query method using func count. Get the count of
        instances by conditions. If target is a class (table), will automatically count primary key.
        :param target: table/column to count from.
        :param condition: filtering conditions.
        :return: the number of matched instances.
        """
        if issubclass(target, self.Base):
            target = inspect(target).primary_key[0]
        with auto_scope(self._session) as _db_session:
            return _db_session.query(func.count(target)).filter(condition).scalar()

    def update(self, target, condition=True, **kwargs):
        """
        Encapsulate sqlalchemy's database session (after auto scoping)'s query method with update enabled. Update
        instances by conditions and values. Should pass in a keyword argument "values".
        :param target: table/column to count from.
        :param condition: filtering conditions.
        :param kwargs: key "values": values dict to update.
        :return: affected rows (0 means update fails either due to wrong condition or wrong values dict).
        """
        with auto_scope(self._session) as _db_session:
            values = kwargs.get("values")  # "values" is a dict
            if values:
                return _db_session.query(target).filter(condition).update(values)

    def close(self):
        """
        Remove database session.
        :return: None.
        """
        self._session.remove()


class dbFactory:
    @staticmethod
    def produce():
        """
        Standard function for production of instance of myDB class.
        :return: a myDb instance.
        """
        return myDb()


my_db = dbFactory.produce()


def init_db(app):
    """
    Initialize (connect and create tables) database for Flask app.
    :param app: Flask app instance.
    :return: None.
    """
    db_path = app.config['DATABASE_PATH']
    my_db.initialize(db_path=db_path)
