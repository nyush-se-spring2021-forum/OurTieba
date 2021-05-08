import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PickleType
from sqlalchemy.orm import relationship

from ..database import my_db


class History(my_db.Base):
    __tablename__ = "history"

    Uid = Column(Integer, ForeignKey("user.Uid"), primary_key=True)
    Pid = Column(Integer, ForeignKey("post.Pid", ondelete='CASCADE'), primary_key=True)
    LastVisitTime = Column(DateTime, default=datetime.datetime.utcnow)

    by_user = relationship("User", back_populates="user")
    related_post = relationship("Post", back_populates="post")

    def __init__(self, Uid, Pid, LastVisitTime=None):
        if isinstance(LastVisitTime, str):
            timestamp = datetime.datetime.strptime(LastVisitTime, "%Y-%m-%d %H:%M:%S")
        self.Uid = Uid
        self.Pid = Pid
        self.LastVisitTime = LastVisitTime

    def __repr__(self):
        return f"<ViewHistory ({self.Uid, self.Pid})>"