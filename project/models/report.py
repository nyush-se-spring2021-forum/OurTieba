import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ._tables import user_report_table
from ..database import my_db


class Report(my_db.Base):
    __tablename__ = "report"

    Rid = Column(Integer, primary_key=True)
    target = Column(String)
    targetId = Column(Integer)  # can be Pid or Cid, for simplicity no foreignkey constraints nor relationship
    reason = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    resolved = Column(Integer, default=0)  # 0=False, 1=True
    Uid = Column(Integer, ForeignKey("user.Uid"))  # reporter

    report_by = relationship("User", secondary=lambda: user_report_table, back_populates="reports")

    def __init__(self, Uid, target, targetId, reason, timestamp=None, resolved=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.Uid = Uid
        self.target = target
        self.targetId = targetId
        self.reason = reason
        self.timestamp = timestamp
        self.resolved = resolved

    def __repr__(self):
        return "<Report %r>" % self.Rid