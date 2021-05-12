import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import my_db


class History(my_db.Base):
    __tablename__ = "history"

    Uid = Column(Integer, ForeignKey("user.Uid"), primary_key=True)
    Pid = Column(Integer, ForeignKey("post.Pid", ondelete='CASCADE'), primary_key=True)
    lastVisitTime = Column(DateTime, default=datetime.datetime.utcnow)

    by_user = relationship("User", back_populates="view")
    related_post = relationship("Post", back_populates="view")

    def __init__(self, Uid, Pid, lastVisitTime=None):
        if isinstance(lastVisitTime, str):
            lastVisitTime = datetime.datetime.strptime(lastVisitTime, "%Y-%m-%d %H:%M:%S")
        self.Uid = Uid
        self.Pid = Pid
        self.lastVisitTime = lastVisitTime

    def __repr__(self):
        return f"<ViewHistory ({self.Uid, self.Pid})>"