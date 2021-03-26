import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Post(Base):
    __tablename__ = "post"

    Pid = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.now())
    commentCount = Column(Integer, default=0)
    likeCount = Column(Integer, default=0)
    dislikeCount = Column(Integer, default=0)
    latestreply = Column(DateTime, default=datetime.datetime.now())
    Uid = Column(Integer, ForeignKey("user.Uid"))
    Bid = Column(Integer, ForeignKey("board.Bid"))

    under = relationship("Board", back_populates="posts")
    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="comment_in")

    def __init__(self, Uid, Bid, title, content, timestamp=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.Uid = Uid
        self.Bid = Bid
        self.title = title
        self.content = content
        self.timestamp = timestamp

    def __repr__(self):
        return '<Post %r>' % self.Pid
