import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey, and_
from sqlalchemy.orm import relationship

from .baseORM import BaseORM
from .board import Board
from ..database import my_db


class Subscription(BaseORM, my_db.Base):
    """
    Mapping of table "subscription".
    """
    __tablename__ = "subscription"

    Uid = Column(Integer, ForeignKey("user.Uid"), primary_key=True)
    Bid = Column(Integer, ForeignKey("board.Bid"), primary_key=True)
    # Two implementations:
    # 1. Not use "subscribed" column. Simply delete from table when unsubscribe;
    # 2. Use "subscribed" column. Set subscribed = 0 when unsubscribe.
    subscribed = Column(Integer, default=0)  # 0 = False, 1 = True,
    lastModified = Column(DateTime, default=datetime.datetime.utcnow)  # timestamp of last action

    by_user = relationship("User", back_populates="subscriptions")
    of_board = relationship("Board", back_populates="subscribers")

    def __init__(self, Uid, Bid, subscribed=None, lastModified=None):
        if isinstance(lastModified, str):
            lastModified = datetime.datetime.strptime(lastModified, "%Y-%m-%d %H:%M:%S")
        self.Uid = Uid
        self.Bid = Bid
        self.subscribed = subscribed
        self.lastModified = lastModified

    def __repr__(self):
        return f"<Subscription ({self.Uid}, {self.Bid})>"

    @classmethod
    def subs_by_user(cls, Uid, Bid):
        """
        Get current subscription status by Uid and Bid. If status not exists, will return 0.
        :param Uid: user ID.
        :param Bid: board ID.
        :return: current status (subscribed).
        """
        subs = cls._get(Uid, Bid)
        if not subs:
            return 0
        return subs.subscribed

    @classmethod
    def user_subs_count(cls, Uid):
        """
        Get user's valid subscription count. The board must be at normal status to be count as valid.
        :param Uid: user ID.
        :return: the number of valid subscriptions.
        """
        count = cls.join_count(Board, and_(Subscription.Uid == Uid, Subscription.subscribed == 1))
        return count

    @classmethod
    def needs_update(cls, Uid, Bid, action):
        """
        Indicate whether "subscribed" needs to be updated on user subscription, since the system allows user to
        subscribe an already subscribed board.
        :param Uid: user ID.
        :param Bid: board ID.
        :param action: 0 (unsubscribe) or 1 (subscribe).
        :return: the span "subscribed" has to update (0, 1, or -1).
        """
        subs = cls._get(Uid, Bid)
        if subs and subs.subscribed == action:  # do not update if no subs record or subs matches action
            return 0
        return 1 if action == 1 else -1  # else return update on subs count