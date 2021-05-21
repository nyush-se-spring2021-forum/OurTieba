import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ._tables import user_report_table
from .baseORM import BaseORM
from ..database import my_db


class Report(BaseORM, my_db.Base):
    """
    Mapping of table "report".

    Attributes:
        Rid: report ID
        target: the report target ("comment" or "post")
        targetId: target's ID
        reason: the reason why the user wants to report this target
        timestamp: time of the report
        resolved: whether the report has been resolved, 0 = False, 1 = True
        Uid: ID of user who report the target
    """
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

    @classmethod
    def get_unresolved_reports_info_by_page(cls, page_num, page_size, order):
        """
        Get info list of unresolved reports by pagination.
        :param page_num: indicates from which page to fetch.
        :param page_size: how many results on one page.
        :param order: by what order the reports are sorted.
        :return: report info list.
        """
        reports = cls._query(cls.resolved == 0, order=order, limit=page_size, offset=(page_num - 1) * page_size)
        report_info_list = []
        for r in reports:
            report_info = {"Rid": r.Rid, "target": r.target, "target_ID": r.targetId, "reason": r.reason,
                           "timestamp": r.timestamp, "Uid": r.Uid}
            report_info_list.append(report_info)
        return report_info_list

    @classmethod
    def count_unresolved_reports(cls):
        """
        Get the number of unresolved (resolved=0) reports.
        :return: the number of unresolved reports.
        """
        number = cls.count(cls.resolved == 0)
        return number

    @classmethod
    def resolve(cls, Rid):
        """
        Resolve a report by Rid. If report not exists, will return error message.
        :param Rid: report ID.
        :return: error message on failure, or success message on success.
        """
        report = cls._get(Rid)
        if not report:
            error = {"error": {"msg": "Report not found."}, "status": 0}
            return error
        cls.update(cls.Rid == Rid, values={"resolved": 1})
        success = {'status': 1}
        return success
