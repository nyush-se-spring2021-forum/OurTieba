import time

from sqlalchemy import Column, Integer, String, DECIMAL

from ..database import my_db


class Notification(my_db.Base):
    __tablename__ = "notification"

    Nid = Column(Integer, primary_key=True)
    # All the columns are NOT nullable!
    starter = Column(String)  # "user", "admin"
    Sid = Column(Integer)  # starter's Uid or Aid
    receiver = Column(String)  # "user", "broadcast"(not implemented)
    Rid = Column(Integer)  # receiver's Uid, if broadcast set to -1
    target = Column(String)  # "post", "comment", "user", "board"(not implemented)
    Tid = Column(Integer)  # target's Pid or Cid or Uid or Bid
    action = Column(String)  # "like", "dislike", "comment", "delete", "restore", "ban", "unban", "post"(not implement)
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