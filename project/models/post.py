import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import my_db


class Post(my_db.Base):
    __tablename__ = "post"

    Pid = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.now())
    commentCount = Column(Integer, default=0)
    likeCount = Column(Integer, default=0)
    dislikeCount = Column(Integer, default=0)
    latestCommentTime = Column(DateTime)
    Uid = Column(Integer, ForeignKey("user.Uid"))
    Bid = Column(Integer, ForeignKey("board.Bid"))

    under = relationship("Board", back_populates="posts")
    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="comment_in")
    status_by = relationship("PostStatus", back_populates="on_post")

    def __init__(self, Uid, Bid, title, content, timestamp=None, LCT=None,
                 commentCount=None, likeCount=None, dislikeCount=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        if isinstance(LCT, str):
            LCT = datetime.datetime.strptime(LCT, "%Y-%m-%d %H:%M:%S")
        self.Uid = Uid
        self.Bid = Bid
        self.title = title
        self.content = content
        self.timestamp = timestamp
        self.latestCommentTime = LCT if LCT else self.timestamp
        self.commentCount = commentCount
        self.likeCount = likeCount
        self.dislikeCount = dislikeCount

    def __repr__(self):
        return '<Post %r>' % self.Pid
