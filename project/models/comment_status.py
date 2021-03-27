import datetime

from sqlalchemy import Column, Integer, DateTime

from ..database import Base


# insert/update on "like" or "dislike" actions
class CommentStatus(Base):
    __tablename__ = "comment_status"

    Uid = Column(Integer, primary_key=True)
    Cid = Column(Integer, primary_key=True)
    liked = Column(Integer, default=0)  # 0 = False, 1 = True
    disliked = Column(Integer, default=0)
    lastModified = Column(DateTime, default=datetime.datetime.now())  # timestamp of last action

    def __init__(self, Uid, Cid, liked=None, disliked=None, last_modified=None):
        if isinstance(last_modified, str):
            last_modified = datetime.datetime.strptime(last_modified, "%Y-%m-%d %H:%M:%S")
        self.Uid = Uid
        self.Cid = Cid
        self.liked = liked
        self.disliked = disliked
        self.lastModified = last_modified

    def __repr__(self):
        return f"<CommentStatus ({self.Uid}, {self.Cid})>"