import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Comment(Base):
    __tablename__ = "comment"

    Cid = Column(Integer, primary_key=True)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.now())
    likeCount = Column(Integer, default=0)
    dislikeCount = Column(Integer, default=0)
    Uid = Column(Integer, ForeignKey("user.Uid"))
    Pid = Column(Integer, ForeignKey("post.Pid"))

    comment_by = relationship("User", back_populates="comments")
    comment_in = relationship("Post", back_populates="comments")

    def __init__(self, Uid, Pid, content, timestamp=None, likeCount=None, dislikeCount=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.Uid = Uid
        self.Pid = Pid
        self.content = content
        self.timestamp = timestamp
        self.likeCount = likeCount
        self.dislikeCount = dislikeCount

    def __repr__(self):
        return '<Post %r>' % self.Pid