import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PickleType
from sqlalchemy.orm import relationship

from ..database import my_db


class Comment(my_db.Base):
    __tablename__ = "comment"

    Cid = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    floor = Column(Integer, nullable=False)  # floor number given by post's available_floor on creation by time order
    medias = Column(PickleType, default=[])  # parsed from "content" column (see api.add_comment)
    text = Column(String, default="")  # plain text in "content" column
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(Integer, default=0)  # 0=normal, 1=deleted(by user), 2=banned(by admin)
    likeCount = Column(Integer, default=0)
    dislikeCount = Column(Integer, default=0)
    Uid = Column(Integer, ForeignKey("user.Uid"))
    Pid = Column(Integer, ForeignKey("post.Pid", ondelete='CASCADE'))

    comment_by = relationship("User", back_populates="comments")
    comment_in = relationship("Post", back_populates="comments")
    status_by = relationship("CommentStatus", back_populates="on_comment", cascade='all, delete', passive_deletes=True)

    def __init__(self, Uid, Pid, content, floor, medias=None, text=None, timestamp=None, status=None, likeCount=None,
                 dislikeCount=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.Uid = Uid
        self.Pid = Pid
        self.content = content
        self.floor = floor
        self.medias = medias
        self.text = text
        self.timestamp = timestamp
        self.status = status
        self.likeCount = likeCount
        self.dislikeCount = dislikeCount

    def __repr__(self):
        return '<Comment %r>' % self.Cid
