import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PickleType
from sqlalchemy.orm import relationship

from .baseORM import BaseORM
from ..configs.macros import STATUS_NORMAL


class Post(BaseORM, my_db.Base):
    __tablename__ = "post"

    Pid = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, default="<p></p>")
    medias = Column(PickleType, default=[])  # parsed from "content" column (see api.add_post)
    text = Column(String, default="")  # plain text in "content" column
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    # next available index for a floor in the post, increment on comment creation, DO NOT decrement on comment deletion
    availableFloor = Column(Integer, default=2)  # available_floor - 1 is the number of comments ever posted in a post
    status = Column(Integer, default=0)  # 0=normal, 1=deleted(by user), 2=banned(by admin)
    stickyOnTop = Column(PickleType, default=[])  # the list of Cid of comment sticky on top
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
                 viewCount=None, commentCount=None, likeCount=None, dislikeCount=None, available_floor=None,
                 sticky_on_top=None):
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
        self.availableFloor = available_floor
        self.status = status
        self.latestCommentTime = LCT
        self.viewCount = viewCount
        self.commentCount = commentCount
        self.stickyOnTop = sticky_on_top
        self.likeCount = likeCount
        self.dislikeCount = dislikeCount

    def __repr__(self):
        return '<Post %r>' % self.Pid

    @classmethod
    def get_info_list_by_page(cls, page_num, page_size, key, order, preview=False):
        posts = cls._query(cls.Bid == key, order=order, limit=page_size, offset=(page_num - 1) * page_size)
        post_info_list = []
        for p in posts:
            post_info = {"Pid": p.Pid, "Uid": p.Uid, "title": p.title, "summary": p.text,
                         "publish_time": p.timestamp, "comment_count": p.commentCount, "like_count": p.likeCount,
                         "dislike_count": p.dislikeCount, "max_floor": p.availableFloor,
                         "preview_type": None, "preview_src": None}
            if preview and p.medias:
                preview_media = p.medias[0].split("/")
                post_info.update({"preview_type": preview_media[0], "preview_src": preview_media[1]})
            post_info_list.append(post_info)
        return post_info_list

    @classmethod
    def get_info_and_board_info(cls, Pid, increment_view=False):
        post = cls._get(Pid)
        if not post:
            return None
        if increment_view:
            post.viewCount += 1
        post_info = {"Pid": post.Pid, "Bid": post.Bid, "Uid": post.Uid, "title": post.title, "content": post.content,
                     "publish_time": post.timestamp, "comment_count": post.commentCount, "like_count": post.likeCount,
                     "dislike_count": post.dislikeCount, "owner": (o := post.owner).nickname, "avatar": o.avatar}
        # do not need to check board's status because post is valid means board is valid
        board_info = {"cover": (b := post.under).cover, "bname": b.name}
        return post_info, board_info

    @classmethod
    def get_medias(cls, Pid):
        post = cls._get(Pid)
        if not post:
            return None
        return post.medias

    @classmethod
    def get_comment_medias(cls, Pid):  # Pid is valid because this follows func get_medias
        comments = cls._get(Pid).comments
        comment_medias = []
        for c in comments:
            if c.status == STATUS_NORMAL:
                comment_medias.extend(c.medias)
        return comment_medias
