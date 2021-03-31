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
    timestamp = Column(DateTime, default=datetime.datetime.now())

    posts = relationship("Post", back_populates="under")

    def __init__(self, name, hot=None, postCount=None, timestamp=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.name = name
        self.hot = hot
        self.postCount = postCount
        self.timestamp = timestamp

    def __repr__(self):
        return "<Board %r>" % self.Bid