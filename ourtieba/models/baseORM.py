from sqlalchemy import inspect, and_

from ..configs.macros import STATUS_NORMAL, STATUS_DELETED, STATUS_BANNED
from ..database import my_db


class BaseORM:
    """
    Contains methods available for all mapped classes to simplify programming. Most of them assumes fetching objects
    with normal status so that need not to specify status in query condition in real code.
    """

    @classmethod
    def _get(cls, *key_value, status=STATUS_NORMAL):
        """
        Get instance by primary key(s), will return either exactly one result or None. Since the return is a database
        object, the method should be private (i.e. should not use this function in any view functions).
        :param key_value: primary key(s) value(s).
        :param status: the status that represents whether an object is deleted or not. Default is STATUS_NORMAL.
        :return: a database object (an instance of cls) whose primary key(s) equal key_value, or None.
        """
        if not cls.__dict__.get("status"):
            return my_db.get(cls, key_value)
        keys = inspect(cls).primary_key
        cond = (keys[i] == key_value[i] for i in range(len(keys)))
        return my_db.query(cls, and_(cls.status == status, and_(cond)), first=True)

    @classmethod
    def exists(cls, *key_value, status=STATUS_NORMAL):
        """
        Check whether an instance whose primary key(s) equal key_value exists or not.
        :param key_value: same as _get.
        :param status: same as _get.
        :return: True=existent or False=non-existent.
        """
        return not not cls._get(*key_value, status=status)  # double negate to obtain Boolean value

    @classmethod
    def new(cls, *cols, **kw_cols):
        """
        Add a new instance to table. If argument already an instance, directly add it to database; otherwise create
        from arguments then add.
        :param cols: instance or values of columns of instance.
        :return: whether add succeeds (affected rows, either 1=success or 0=failure).
        """
        if type((_new := cols[0])) == type(cls):
            return my_db.add(_new)
        # Same as:
        # cls.__init__((new_instance := cls.__new__(cls)), *args, **kwargs)
        # return my_db.add(new_instance)
        return my_db.add(cls(*cols, **kw_cols))

    @classmethod
    def _query(cls, *conditions, status=STATUS_NORMAL, **kw_conditions):
        """
        Get instances with status by conditions (i.e. filter, order, limit, offset etc.). Default status is normal(0).
        conditions[0] is the positional argument "condition" in func my_db.query.
        :param conditions: conditions passed in as positional arguments.
        :param status: the status that represents whether an object is deleted or not. Default is STATUS_NORMAL.
        :param kw_conditions: conditions passed in as keyword arguments.
        :return: list of database objects (instances of cls) whose conditions match those in arguments, or [].
        """
        if not cls.__dict__.get("status"):
            return my_db.query(cls, *conditions, **kw_conditions)
        if not conditions:
            return my_db.query(cls, cls.status == status, **kw_conditions)
        return my_db.query(cls, and_(cls.status == status, conditions[0]), *conditions[1:], **kw_conditions)

    @classmethod
    def query_exists(cls, *conditions, status=STATUS_NORMAL, **kw_conditions):
        """
        Check whether instances with status whose conditions match those in arguments exist or not. Default status is
        normal(0).
        :param conditions: conditions passed in as positional arguments.
        :param status: the status that represents whether an object is deleted or not. Default is STATUS_NORMAL.
        :param kw_conditions: conditions passed in as keyword arguments.
        :return: True=existent or False=non-existent.
        """
        return not not cls._query(*conditions, status=status, **kw_conditions)

    @classmethod
    def count(cls, *conditions, status=STATUS_NORMAL, **kw_conditions):
        """
        Get the number of instances with status by conditions (i.e. filter, order, limit, offset etc.). Default status
        is normal(0). conditions[0] is the positional argument "condition" in func my_db.query.
        :param conditions: conditions passed in as positional arguments.
        :param status: the status that represents whether an object is deleted or not. Default is STATUS_NORMAL.
        :param kw_conditions: conditions passed in as keyword arguments.
        :return: number of database objects (instances of cls) whose conditions match those in arguments.
        """
        if not cls.__dict__.get("status"):
            return my_db.count(cls, *conditions, **kw_conditions)
        if not conditions:
            return my_db.count(cls, cls.status == status, **kw_conditions)
        return my_db.count(cls, and_(cls.status == status, conditions[0]), *conditions[1:], **kw_conditions)

    @classmethod
    def update(cls, *conditions, status=STATUS_NORMAL, **kw_conditions):
        """
        Update instance with status by conditions and return the number of affected rows. Default status is normal(0).
        conditions[0] is the positional argument "condition" in func my_db.query.
        :param conditions: conditions passed in as positional arguments.
        :param status: the status that represents whether an object is deleted or not. Default is STATUS_NORMAL.
        :param kw_conditions: conditions passed in as keyword arguments.
        :return: number of affected database objects (instances of cls) whose conditions match those in arguments. If 0,
                 update fails.
        """
        if not cls.__dict__.get("status"):
            return my_db.update(cls, *conditions, **kw_conditions)
        if not conditions:
            return my_db.update(cls, cls.status == status, **kw_conditions)
        return my_db.update(cls, and_(cls.status == status, conditions[0]), *conditions[1:], **kw_conditions)

    @classmethod
    def _query_join(cls, *conditions, status=STATUS_NORMAL, **kw_conditions):
        """
        Similar to func _query but allows joining of another table. Default status is normal(0). conditions[0] is the
        table to join, conditions[1] is the positional argument "condition" in func my_db.query.
        :param conditions: conditions passed in as positional arguments.
        :param status: the status that represents whether an object is deleted or not. Default is STATUS_NORMAL.
        :param kw_conditions: conditions passed in as keyword arguments.
        :return: list of instances in joined table whose conditions match those in arguments, or [].
        """
        if not cls.__dict__.get("status"):
            return my_db.query_join(cls, *conditions, **kw_conditions)
        return my_db.query_join(cls, conditions[0], and_(cls.status == status, conditions[1]), *conditions[2:],
                                **kw_conditions)

    @classmethod
    def join_count(cls, *conditions, status=STATUS_NORMAL, **kw_conditions):
        """
        Similar to func count but allows joining of another table. Default status is normal(0).
        :param conditions: conditions passed in as positional arguments.
        :param status: the status that represents whether an object is deleted or not. Default is STATUS_NORMAL.
        :param kw_conditions: conditions passed in as keyword arguments.
        :return: number of instances in joined table whose conditions match those in arguments.
        """
        return cls._query_join(*conditions, count=True, status=status, **kw_conditions)

    @classmethod
    def merge(cls, *cols, **kw_cols):
        """
        Merge (if exists will overwrite, else create new) an instance into table. If argument already an instance,
        directly add it to database; otherwise create from arguments then add.
        :param cols: instance or values of columns of instance.
        :return: whether merge succeeds (affected rows, either 1=success or 0=failure).
        """
        if type((_new := cols[0])) == type(cls):
            return my_db.merge(_new)
        return my_db.merge(cls(*cols, **kw_cols))

    @classmethod
    def _real_delete(cls, *conditions, synchronize_session="fetch", **kw_conditions):
        """
        Delete instances from table by conditions. Will NOT automatically filter status.
        :param conditions: conditions passed in as positional arguments.
        :param synchronize_session: what to do with database session before deletion. "fetch", "evaluate" or False.
        :param kw_conditions: conditions passed in as keyword arguments.
        :return: number of affected instances.
        """
        return my_db.delete(cls, *conditions, synchronize_session=synchronize_session, **kw_conditions)

    @classmethod
    def _delete(cls, *conditions, real_delete=False, **kw_conditions):
        """
        If not real_delete, set all instances' status to STATUS_DELETED if their status is normal by conditions.
        Else delete the instances.
        :param conditions: conditions passed in as positional arguments.
        :param real_delete: whether to actually delete instances.
        :param kw_conditions: conditions passed in as keyword arguments.
        :return: number of affected instances.
        """
        if real_delete:
            return cls._real_delete(*conditions, **kw_conditions)
        return cls.update(*conditions, status=STATUS_NORMAL, values={"status": STATUS_DELETED}, **kw_conditions)

    @classmethod
    def _ban(cls, *conditions, real_delete=False, **kw_conditions):
        """
        If not real_delete, set all instances' status to STATUS_BANNED if their status is normal by conditions.
        Else delete the instances.
        :param conditions: conditions passed in as positional arguments.
        :param real_delete: whether to actually delete instances.
        :param kw_conditions: conditions passed in as keyword arguments.
        :return: number of affected instances.
        """
        if real_delete:
            return cls._real_delete(*conditions, **kw_conditions)
        return cls.update(*conditions, status=STATUS_NORMAL, values={"status": STATUS_BANNED}, **kw_conditions)

    @classmethod
    def _restore(cls, *conditions, by, **kw_conditions):
        """
        Set all instances' status to STATUS_NORMAL by conditions. If restore by user, the instances will be filtered by
        status is deleted else filtered by status is banned.
        :param conditions: conditions passed in as positional arguments.
        :param by: the starter of the action. "user" or "admin".
        :param kw_conditions: conditions passed in as keyword arguments.
        :return: number of affected instances.
        """
        query_status = STATUS_DELETED if by == "user" else STATUS_BANNED
        return cls.update(*conditions, status=query_status, values={"status": STATUS_NORMAL}, **kw_conditions)
