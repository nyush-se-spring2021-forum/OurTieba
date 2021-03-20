import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Post(Base):
    __tablename__ = "post"

    Pid = Column(Integer, primary_key=True)
    title = Column(String(100))
    content = Column(String(500))
    timestamp = Column(DateTime, default=datetime.datetime.now())
    commentCount = Column(Integer, default=0)
    likeCount = Column(Integer, default=0)
    dislikeCount = Column(Integer, default=0)
    Uid = Column(Integer, ForeignKey("user.Uid"))

    owner = relationship("User", back_populates="posts")

    def __init__(self, Uid, title, content, timestamp=None):
        self.Uid = Uid
        self.title = title
        self.content = content
        self.timestamp = timestamp

    def __repr__(self):
        return '<Post %r>' % self.Pid
