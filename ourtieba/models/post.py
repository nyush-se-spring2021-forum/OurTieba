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
    # next available index for a floor in the post, increment on comment creation, DO NOT decrement on comment deletion
    available_floor = Column(Integer, default=2)  # available_floor - 1 is the number of comments ever posted in a post
    status = Column(Integer, default=0)  # 0=normal, 1=deleted(by user), 2=banned(by admin)
    sticky_on_top = Column(PickleType, default=[])  # the list of Cid of comment sticky on top
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
    view = relationship("History", back_populates="related_post")

    def __init__(self, Uid, Bid, title, content=None, medias=None, text=None, timestamp=None, LCT=None, status=None,
                 viewCount=None, commentCount=None, likeCount=None, dislikeCount=None, available_floor=None):
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
        self.available_floor = available_floor
        self.status = status
        self.latestCommentTime = LCT
        self.viewCount = viewCount
        self.commentCount = commentCount
        self.likeCount = likeCount
        self.dislikeCount = dislikeCount

    def __repr__(self):
        return '<Post %r>' % self.Pid
