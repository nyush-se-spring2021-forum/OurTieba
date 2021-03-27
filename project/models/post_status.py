import datetime

from sqlalchemy import Column, Integer, DateTime

from ..database import Base


# insert/update on "like" or "dislike" actions
class PostStatus(Base):
    __tablename__ = "post_status"

    Uid = Column(Integer, primary_key=True)
    Pid = Column(Integer, primary_key=True)
    liked = Column(Integer, default=0)  # 0 = False, 1 = True
    disliked = Column(Integer, default=0)
    lastModified = Column(DateTime, default=datetime.datetime.now())  # timestamp of last action

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