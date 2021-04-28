import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from ..database import my_db


class Board(my_db.Base):
    __tablename__ = "board"

    Bid = Column(Integer, primary_key=True)
    name = Column(String)
    hot = Column(Integer, default=0)
    postCount = Column(Integer, default=0)
    viewCount = Column(Integer, default=0)
    subscribeCount = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    posts = relationship("Post", back_populates="under")
    subscribers = relationship("Subscription", back_populates="of_board")

    def __init__(self, name, hot=None, postCount=None, viewCount=None, subscribeCount=None,
                 timestamp=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.name = name
        self.hot = hot
        self.viewCount = viewCount
        self.subscribeCount = subscribeCount
        self.postCount = postCount
        self.timestamp = timestamp

    def __repr__(self):
        return "<Board %r>" % self.Bid