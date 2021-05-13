from sqlalchemy import inspect, and_

from ..database import my_db


class BaseORM:
    __slots__ = "status"

    @classmethod
    def _get(cls, *key_value, status=None):
        """
        Get instance by primary key(s), will return either exactly one result or None. Since the return is a database
        object, the method should be private (i.e. should not use this function in any view functions).
        :param key_value: primary key(s) value(s).
        :param status: the status that represents whether an object is deleted or not. Default is None.
        :return: a database object (an instance of cls) whose primary key(s) equal key_value, or None.
        """
        if status is None:
            return my_db.get(cls, key_value)
        keys = inspect(cls).primary_key
        cond = (keys[i] == key_value[i] for i in range(len(keys)))
        return my_db.query(cls, and_(cls.status == status, and_(cond)), first=True)

    @classmethod
    def exists(cls, *key_value, status=None):
        """
        Check whether an instance whose primary key(s) equal key_value exists or not.
        :param key_value: same as _get.
        :param status: same as _get.
        :return: True=existent or False=non-existent.
        """
        return not not cls._get(cls, *key_value, status=status)  # double negate to obtain Boolean value

    @classmethod
    def new(cls, *args):
        """
        Add a new instance to class. If argument already an instance, directly add it to database; otherwise create
        from arguments then add.
        :param args: instance or values of columns of instance.
        :return: whether add success (affected rows, either 1=success or 0=failure).
        """
        if type((_new := args[0])) == type(cls):
            return my_db.add(_new)
        return my_db.add(cls(*args))