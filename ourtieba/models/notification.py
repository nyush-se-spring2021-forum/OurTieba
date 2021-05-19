import datetime
import time

from sqlalchemy import Column, Integer, String, and_

from .baseORM import BaseORM
from ..configs.functions import convert_time
from ..database import my_db


class Notification(BaseORM, my_db.Base):
    __tablename__ = "notification"

    Nid = Column(Integer, primary_key=True)
    # All the columns are NOT nullable!
    # (ad) means only starts/receives/acts by admin, AND will NOT be implemented in this version
    starter = Column(String)  # "user", "admin"
    Sid = Column(Integer)  # starter's Uid or Aid
    receiver = Column(String)  # "user", "admin", "broadcast" (ad)
    Rid = Column(Integer)  # receiver's Uid, if broadcast set to -1
    target = Column(String)  # "post", "comment", "user", "board" (ad)
    Tid = Column(Integer)  # target's Pid or Cid or Uid or days (for ban only) or Bid(ad)
    action = Column(String)  # "like", "dislike", "comment", "reply", "delete", "restore", "ban", "unban", "post" (ad)
    timestamp = Column(Integer, default=time.time)  # must be UNIX timestamp, like "1620750628.290329" etc.

    def __init__(self, starter, Sid, receiver, Rid, target, Tid, action, timestamp=None):
        self.starter = starter
        self.Sid = Sid
        self.receiver = receiver
        self.Rid = Rid
        self.target = target
        self.Tid = Tid
        self.action = action
        self.timestamp = timestamp

    @classmethod
    def compose_ntfs(cls, cls_dict, Uid, order, limit, offset, last_check):
        action_dict = {"like": "liked", "dislike": "disliked", "comment": "commented on", "reply": "replied to",
                       "delete": "deleted", "restore": "restored"}
        ntfs = cls._query(and_(cls.receiver == "user", cls.Rid == Uid), order, limit=limit, offset=offset)
        ntf_info_list = []
        for n in ntfs:
            ts = n.timestamp
            utc_time = convert_time(datetime.datetime.utcfromtimestamp(ts))
            ntf_info = {"timestamp": utc_time, "is_new": 1 if last_check < int(ts) < time.time() else 0}

            starter_cls: BaseORM = cls_dict[n.starter]
            starter_name = starter_cls._get(n.Sid).nickname
            action = n.action
            if (is_ban := action == "ban") or action == "unban":
                message = starter_name + " banned" if is_ban else " unbanned" + " you " + \
                                                                  ("for " + n.Tid + " days") if is_ban else "now"
            else:
                target = n.target
                target_cls: BaseORM = cls_dict[target]
                target_row = target_cls._get(n.Tid)
                abstract = target_row.title if target == "post" else target_row.text
                message = starter_name + " " + action_dict[action] + " your " + target + ' "' + abstract + '"'

            ntf_info.update({"message": message})
            ntf_info_list.append(ntf_info)
        return ntf_info_list