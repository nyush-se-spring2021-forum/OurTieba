import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PickleType
from sqlalchemy.orm import relationship

from .baseORM import BaseORM
from .comment_status import CommentStatus
from .report import Report
from .user import User
from ..configs.macros import STATUS_DELETED, STATUS_BANNED
from ..database import my_db


class Comment(BaseORM, my_db.Base):
    """
    Mapping of table "comment".

    Attributes:
        Cid: comment's ID
        content: comment's content
        floor: where the comment locates
        medias: list of the path of every images or videos, [] if no images and videos
        text: plain text in "content" column, not including any images and videos
        timestamp: the time of the comment be created
        status: 0=normal, 1=deleted(by user), 2=banned(by admin)
        likeCount: number of like of this comment
        dislikeCount: number of dislike of this comment
        Uid: the user who created this comment
        Pid: the comment is under this post
    """
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

    @classmethod
    def get_info_list_by_page(cls, page_num, page_size, key, order):
        """
        Get comment info list by key Pid and pagination.
        :param page_num: indicates from which page to fetch.
        :param page_size: how many results on one page.
        :param key: Pid.
        :param order: by what order the comments are sorted.
        :return: comment info list.
        """
        comments = cls._query(cls.Pid == key, order, limit=page_size, offset=(page_num - 1) * page_size)
        comment_info_list = [{"Cid": c.Cid, "Uid": c.Uid, "content": c.content, "publish_time": c.timestamp,
                              "like_count": c.likeCount, "dislike_count": c.dislikeCount,
                              "publish_user": c.comment_by.nickname,
                              "user_avatar": c.comment_by.avatar, "floor": c.floor} for c in comments]
        return comment_info_list

    @classmethod
    def ban_comment(cls, Cid):
        """
        Ban a comment by Cid, and modify comment count. If comment not exists, will return failure (0).
        :param Cid: comment ID.
        :return: failure (0), or Uid of comment owner.
        """
        match_comment: Comment = cls._get(Cid)
        if not match_comment:
            return 0

        match_comment.comment_in.commentCount -= 1
        cls._ban(cls.Cid == Cid)
        return match_comment.Uid

    @classmethod
    def delete_comment(cls, Cid):
        """
        Delete a comment by Cid, and modify comment count. If comment not exists, will return failure (0).
        :param Cid: comment ID.
        :return: failure (0), or Uid of comment owner.
        """
        match_comment = cls._get(Cid)
        if not match_comment:
            return 0

        match_comment.comment_in.commentCount -= 1
        cls._delete(cls.Cid == Cid)
        return match_comment.Uid

    @classmethod
    def restore_comment(cls, Cid, by):
        """
        Restore a comment by Cid, and modify comment count unless it is deleted by user. If comment not exists, will
        return failure (0).
        :param by: who starts this action. "user" or "admin".
        :param Cid: comment ID.
        :return: failure (0), or Uid of comment owner.
        """
        query_status = STATUS_DELETED if by == "user" else STATUS_BANNED
        match_comment = cls._get(Cid, status=query_status)
        if not match_comment:
            return 0

        match_comment.comment_in.commentCount += 1
        cls._restore(cls.Cid == Cid, by=by)
        return match_comment.Uid

    @classmethod
    def like(cls, Cid, Uid):
        """
        Like a comment, and update like/dislike count. This action assumes user perform opposite operation on current
        status, so whether to like/unlike is automatically decided. If comment not exists, return 0.
        :param Cid: comment ID.
        :param Uid: user ID.
        :return: 0 if post not exists, or current comment status.
        """
        match_comment = cls._get(Cid)
        if not match_comment:
            return 0

        match_status = CommentStatus._get(Uid, Cid)
        if not match_status:
            cur_status = 1
            CommentStatus.new(Uid, Cid, cur_status, 0)
            cur_like = match_comment.likeCount + 1
            cur_dislike = match_comment.dislikeCount
        else:
            liked = match_status.liked
            disliked = match_status.disliked
            cur_status = 0 if liked else 1
            CommentStatus.merge(Uid, Cid, cur_status, 0, datetime.datetime.utcnow())
            cur_like = match_comment.likeCount + -1 if liked else 1
            cur_dislike = match_comment.dislikeCount - 1 if disliked else 0

        cls.update(cls.Cid == Cid, values={"likeCount": cur_like, "dislikeCount": cur_dislike})
        return {"cur_status": cur_status, "like_count": cur_like, "dislike_count": cur_dislike,
                "Rid": match_comment.Uid}

    @classmethod
    def dislike(cls, Cid, Uid):
        """
        Dislike a comment, and update like/dislike count. This action assumes user perform opposite operation on current
        status, so whether to dislike/undislike is automatically decided. If comment not exists, return 0.
        :param Cid: comment ID.
        :param Uid: user ID.
        :return: 0 if post not exists, or current comment status.
        """
        match_comment = cls._get(Cid)
        if not match_comment:
            return 0

        match_status = CommentStatus._get(Uid, Cid)
        if not match_status:
            cur_status = 1
            CommentStatus.new(Uid, Cid, 0, cur_status)
            cur_like = match_comment.likeCount
            cur_dislike = match_comment.dislikeCount + 1
        else:
            liked = match_status.liked
            disliked = match_status.disliked
            cur_status = 0 if disliked else 1
            CommentStatus.merge(Uid, Cid, 0, cur_status, datetime.datetime.utcnow())
            cur_like = match_comment.likeCount - 1 if disliked else 0
            cur_dislike = match_comment.dislikeCount + -1 if liked else 1

        cls.update(cls.Cid == Cid, values={"likeCount": cur_like, "dislikeCount": cur_dislike})
        return {"cur_status": cur_status, "like_count": cur_like, "dislike_count": cur_dislike,
                "Rid": match_comment.Uid}

    @classmethod
    def report(cls, Uid, Cid, reason):
        """
        Add report of a comment. If comment not exists, return error message.
        :param Uid: reporter ID.
        :param Cid: comment ID.
        :param reason: reason of report.
        :return: error message on failure, or success message on success.
        """
        match_comment = cls._get(Cid)
        if not match_comment:
            error = {"error": {"msg": "Invalid target ID."}, "status": 0}
            return error

        new_report = Report(Uid, "comment", Cid, reason)
        reporter = User._get(Uid)
        reporter.reports.append(new_report)
        Report.new(Uid, "comment", Cid, reason)
        success = {"status": 1}
        return success
