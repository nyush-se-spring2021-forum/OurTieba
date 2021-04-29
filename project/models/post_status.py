import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import my_db


# insert/update on "like" or "dislike" actions
class PostStatus(my_db.Base):
    __tablename__ = "post_status"

    Uid = Column(Integer, ForeignKey("user.Uid"), primary_key=True)
    Pid = Column(Integer, ForeignKey("post.Pid", ondelete='CASCADE'), primary_key=True)
    liked = Column(Integer, default=0)  # 0 = False, 1 = True
    disliked = Column(Integer, default=0)
    lastModified = Column(DateTime, default=datetime.datetime.utcnow)  # timestamp of last action

    by_user = relationship("User", back_populates="status_post")
    on_post = relationship("Post", back_populates="status_by")

    def __init__(self, Uid, Pid, liked=None, disliked=None, lastModified=None):
        if isinstance(lastModified, str):
            lastModified = datetime.datetime.strptime(lastModified, "%Y-%m-%d %H:%M:%S")
        self.Uid = Uid
        self.Pid = Pid
        self.liked = liked
        self.disliked = disliked
        self.lastModified = lastModified

    def __repr__(self):
        return f"<PostStatus ({self.Uid}, {self.Pid})>"