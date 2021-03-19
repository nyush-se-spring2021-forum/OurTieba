from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
import datetime


class Post(Base):
    __tablename__ = "post"

    Pid = Column(Integer, primary_key=True)
    title = Column(String(100))
    content = Column(String(500))
    timestamp = Column(DateTime, default=datetime.datetime.now())
    commentCount = Column(Integer, default=0)
    likeCount = Column(Integer, default=0)
    dislikeCount = Column(Integer, default=0)

    def __init__(self, title, content, timestamp=None):
        self.title = title
        self.content = content
        self.timestamp = timestamp

    def __repr__(self):
        return '<User %r>' % self.Pid
