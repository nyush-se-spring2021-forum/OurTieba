import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .baseORM import BaseORM
from ..database import my_db


# insert/update on "like" or "dislike" actions
class CommentStatus(BaseORM, my_db.Base):
    """
    Mapping of table "comment_status".
    """
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

    @classmethod
    def status_by_user(cls, Uid, Cid):
        """
        Get current status by Uid and Cid. If status not exists, will return 0, 0.
        :param Uid: user ID.
        :param Cid: comment ID.
        :return: current comment status (liked, disliked) in tuple.
        """
        status = cls._get(Uid, Cid)
        if not status:
            return 0, 0
        return status.liked, status.disliked
