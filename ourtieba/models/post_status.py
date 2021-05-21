import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .baseORM import BaseORM
from ..database import my_db


# insert/update on "like" or "dislike" actions
class PostStatus(BaseORM, my_db.Base):
    """
    Mapping of table "post_status".

    Attributes:
        Uid: the user who is going to do the like/dislike operation
        Pid: the post ID which is going to be liked/disliked
        liked: 0 = this user doesn't like this post, 1 = this user likes this post
        disliked: 0 = this user doesn't dislike this post, 1 = this user dislikes this post
        lastModified: time of last action
    """
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

    @classmethod
    def status_by_user(cls, Uid, Pid):
        """
        Get current post status by Uid and Pid. If status not exists, will return 0, 0.
        :param Uid: user ID.
        :param Pid: post ID.
        :return: current status (liked, disliked) in tuple.
        """
        status = cls._get(Uid, Pid)
        if not status:
            return 0, 0
        return status.liked, status.disliked
