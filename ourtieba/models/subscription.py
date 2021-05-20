import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .baseORM import BaseORM
from ..database import my_db


class Subscription(BaseORM, my_db.Base):
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
        subs = cls._get(Uid, Bid)
        if not subs:
            return 0
        return subs.subscribed

    @classmethod
    def needs_update(cls, Uid, Bid, action):
        subs = cls._get(Uid, Bid)
        if subs and subs.subscribed == action:  # do not update if no subs record or subs matches action
            return 0
        return 1 if action == 1 else -1  # else return update on subs count