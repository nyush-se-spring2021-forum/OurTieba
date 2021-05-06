import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PickleType
from sqlalchemy.orm import relationship

from ..database import my_db


class Post(my_db.Base):
    __tablename__ = "post"

    Pid = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, default="<p></p>")
    medias = Column(PickleType, default=[])  # parsed from "content" column (see api.add_post)
    text = Column(String, default="")  # plain text in "content" column
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    commentCount = Column(Integer, default=0)
    likeCount = Column(Integer, default=0)
    dislikeCount = Column(Integer, default=0)
    viewCount = Column(Integer, default=0)
    latestCommentTime = Column(DateTime, default=datetime.datetime.utcnow)

    Uid = Column(Integer, ForeignKey("user.Uid"))
    Bid = Column(Integer, ForeignKey("board.Bid"))

    under = relationship("Board", back_populates="posts")
    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="comment_in", cascade='all, delete', passive_deletes=True)
    status_by = relationship("PostStatus", back_populates="on_post", cascade='all, delete', passive_deletes=True)

    def __init__(self, Uid, Bid, title, content=None, medias=None, text=None, timestamp=None, LCT=None,
                 viewCount=None, commentCount=None, likeCount=None, dislikeCount=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        if isinstance(LCT, str):
            LCT = datetime.datetime.strptime(LCT, "%Y-%m-%d %H:%M:%S")
        self.Uid = Uid
        self.Bid = Bid
        self.title = title
        self.content = content
        self.medias = medias
        self.text = text
        self.timestamp = timestamp
        self.latestCommentTime = LCT
        self.viewCount = viewCount
        self.commentCount = commentCount
        self.likeCount = likeCount
        self.dislikeCount = dislikeCount

    def __repr__(self):
        return '<Post %r>' % self.Pid
