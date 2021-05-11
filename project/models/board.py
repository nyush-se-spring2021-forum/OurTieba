import datetime

from sqlalchemy import Column, Integer, String, DateTime, PickleType
from sqlalchemy.orm import relationship

from ..database import my_db


class Board(my_db.Base):
    __tablename__ = "board"

    Bid = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    hot = Column(Integer, default=0)
    cover = Column(String, default="cover/OurTieba.png")
    status = Column(Integer, default=0)  # 0=normal, 1=deleted(by user), 2=banned(by admin)
    sticky_on_top = Column(PickleType, default=[])  # the list of Pid of post sticky on top
    postCount = Column(Integer, default=0)
    viewCount = Column(Integer, default=0)
    subscribeCount = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    posts = relationship("Post", back_populates="under")
    subscribers = relationship("Subscription", back_populates="of_board")

    def __init__(self, name, description, hot=None, cover=None, status=None, sticky_on_top=None, postCount=None,
                 viewCount=None, subscribeCount=None, timestamp=None, ):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.name = name
        self.description = description
        self.hot = hot
        self.cover = cover
        self.status = status
        self.sticky_on_top = sticky_on_top
        self.viewCount = viewCount
        self.subscribeCount = subscribeCount
        self.postCount = postCount
        self.timestamp = timestamp

    def __repr__(self):
        return "<Board %r>" % self.Bid