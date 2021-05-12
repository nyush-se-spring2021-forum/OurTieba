import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import my_db


# insert/update on "like" or "dislike" actions
class CommentStatus(my_db.Base):
    __tablename__ = "comment_status"

    Uid = Column(Integer, ForeignKey("user.Uid"), primary_key=True)
    Cid = Column(Integer, ForeignKey("comment.Cid", ondelete='CASCADE'), primary_key=True)
    liked = Column(Integer, default=0)  # 0 = False, 1 = True
    disliked = Column(Integer, default=0)
    lastModified = Column(DateTime, default=datetime.datetime.utcnow)  # timestamp of last action

    by_user = relationship("User", back_populates="status_comment")
    on_comment = relationship("Comment", back_populates="status_by")

    def __init__(self, Uid, Cid, liked=None, disliked=None, lastModified=None):
        if isinstance(lastModified, str):
            lastModified = datetime.datetime.strptime(lastModified, "%Y-%m-%d %H:%M:%S")
        self.Uid = Uid
        self.Cid = Cid
        self.liked = liked
        self.disliked = disliked
        self.lastModified = lastModified

    def __repr__(self):
        return f"<CommentStatus ({self.Uid}, {self.Cid})>"