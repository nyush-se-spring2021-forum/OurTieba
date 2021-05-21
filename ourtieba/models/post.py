import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PickleType
from sqlalchemy.orm import relationship

from .baseORM import BaseORM
from .comment import Comment
from .notification import Notification
from .post_status import PostStatus
from .report import Report
from .user import User
from ..configs.macros import STATUS_NORMAL, STATUS_DELETED, STATUS_BANNED
from ..database import my_db


class Post(BaseORM, my_db.Base):
    """
    Mapping of table "post". Note: "stickyOnTop" not implemented, "viewCount" not reflected on web page.
    """
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
        """
        Get post info list by key Bid and pagination, also add preview info if specified.
        :param preview: whether to fetch preview info.
        :param page_num: indicates from which page to fetch.
        :param page_size: how many results on one page.
        :param key: Bid.
        :param order: by what order the posts are sorted.
        :return: post info list.
        """
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
        """
        Get post info by Pid and corresponding board info, also increment view count if specified. If post not exists,
        will return None.
        :param Pid: post ID
        :param increment_view: whether to increment view count.
        :return: post info dict and board info dict (as a tuple).
        """
        post = cls._get(Pid)
        if not post:
            return None, None
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
        """
        Get media list of post by Pid. If post not exists, will return None.
        :param Pid: post ID.
        :return: media list of the post.
        """
        post = cls._get(Pid)
        if not post:
            return None
        return post.medias

    @classmethod
    def get_comment_medias(cls, Pid):
        """
        Get media list of comments in a post by Pid. Pid is for sure valid because this function is called only when
        func get_medias does not return None.
        :param Pid: post ID.
        :return: media list of comments in the post.
        """
        comments = cls._get(Pid).comments
        comment_medias = []
        for c in comments:
            if c.status == STATUS_NORMAL:
                comment_medias.extend(c.medias)
        return comment_medias

    @classmethod
    def ban_post(cls, Pid):
        """
        Ban a post by Pid, and modify post count. Will also ban all comments under it. If post not exists, will return
        failure (0).
        :param Pid: post ID.
        :return: failure (0), or Uid of post owner.
        """
        match_post = cls._get(Pid)
        if not match_post:
            return 0

        match_post.under.postCount -= 1
        cls._ban(cls.Pid == Pid)
        for c in match_post.comments:
            Comment._ban(Comment.Cid == c.Cid)
        return match_post.Uid

    @classmethod
    def delete_post(cls, Pid):
        """
        Delete a post by Pid, and modify comment count. Will also delete all comments under it. If post not exists,
        will return failure (0).
        :param Pid: post ID.
        :return: failure (0), or Uid of post owner.
        """
        match_post = cls._get(Pid)
        if not match_post:
            return 0

        match_post.under.postCount -= 1
        cls._delete(cls.Pid == Pid)
        for c in match_post.comments:
            Comment._delete(Comment.Cid == c.Cid)
        return match_post.Uid

    @classmethod
    def restore_post(cls, Pid, by):
        """
        Restore a post by Pid, and modify comment count. Will also restore all comments under it (unless deleted by user
        ). If post not exists, will return failure (0).
        :param by: who starts this action. "user" or "admin".
        :param Pid: post ID.
        :return: failure (0), or Uid of post owner.
        """
        query_status = STATUS_DELETED if by == "user" else STATUS_BANNED
        match_post = cls._get(Pid, status=query_status)
        if not match_post:
            return 0

        match_post.under.postCount += 1
        cls._restore(cls.Pid == Pid, by=by)
        for c in match_post.comments:
            Comment._restore(Comment.Cid == c.Cid, by=by)
        return match_post.Uid

    @classmethod
    def like(cls, Pid, Uid):
        """
        Like a post, and update like/dislike count. This action assumes user perform opposite operation on current
        status, so whether to like/unlike is automatically decided. If post not exists, return 0.
        :param Pid: post ID.
        :param Uid: user ID.
        :return: 0 if post not exists, or current post status.
        """
        match_post = cls._get(Pid)
        if not match_post:
            return 0

        match_status = PostStatus._get(Uid, Pid)
        if not match_status:
            cur_status = 1
            PostStatus.new(Uid, Pid, cur_status, 0)
            cur_like = match_post.likeCount + 1
            cur_dislike = match_post.dislikeCount
        else:
            liked = match_status.liked
            disliked = match_status.disliked
            cur_status = 0 if liked else 1
            PostStatus.merge(Uid, Pid, cur_status, 0, datetime.datetime.utcnow())
            cur_like = match_post.likeCount + -1 if liked else 1
            cur_dislike = match_post.dislikeCount - 1 if disliked else 0

        cls.update(cls.Pid == Pid, values={"likeCount": cur_like, "dislikeCount": cur_dislike})
        return {"cur_status": cur_status, "like_count": cur_like, "dislike_count": cur_dislike,
                "Rid": match_post.Uid}

    @classmethod
    def dislike(cls, Pid, Uid):
        """
        Dislike a post, and update like/dislike count. This action assumes user perform opposite operation on current
        status, so whether to dislike/undislike is automatically decided. If post not exists, return 0.
        :param Pid: post ID.
        :param Uid: user ID.
        :return: 0 if post not exists, or current post status.
        """
        match_post = cls._get(Pid)
        if not match_post:
            return 0

        match_status = PostStatus._get(Uid, Pid)
        if not match_status:
            cur_status = 1
            PostStatus.new(Uid, Pid, 0, cur_status)
            cur_like = match_post.likeCount
            cur_dislike = match_post.dislikeCount + 1
        else:
            liked = match_status.liked
            disliked = match_status.disliked
            cur_status = 0 if disliked else 1
            PostStatus.merge(Uid, Pid, 0, cur_status, datetime.datetime.utcnow())
            cur_like = match_post.likeCount - 1 if liked else 0
            cur_dislike = match_post.dislikeCount + -1 if disliked else 1

        cls.update(cls.Pid == Pid, values={"likeCount": cur_like, "dislikeCount": cur_dislike})
        return {"cur_status": cur_status, "like_count": cur_like, "dislike_count": cur_dislike,
                "Rid": match_post.Uid}

    @classmethod
    def report(cls, Uid, Pid, reason):
        """
        Add report of a post. If post not exists, return error message.
        :param Uid: reporter ID.
        :param Pid: post ID.
        :param reason: reason of report.
        :return: error message on failure, or success message on success.
        """
        match_post = cls._get(Pid)
        if not match_post:
            error = {"error": {"msg": "Invalid target ID."}, "status": 0}
            return error

        new_report = Report(Uid, "post", Pid, reason)
        reporter = User._get(Uid)
        reporter.reports.append(new_report)
        Report.new(Uid, "post", Pid, reason)
        success = {"status": 1}
        return success

    @classmethod
    def add_comment(cls, Pid, Uid, reply_ele, text, medias):
        """
        Add comment to database and send necessary notifications. If post not exists, return 0. If reply is empty,
        return -1.
        :param Pid: post ID.
        :param Uid: user ID.
        :param reply_ele: html element of reply.
        :param text: comment text.
        :param medias: list of medias in comment.
        :return: the floor of comment if add successful else 0 or -1 on failures.
        """
        match_post = cls._get(Pid)
        if not match_post:
            return 0

        if reply_ele:
            ele_text_length = len(reply_ele.text)
            if len(text) <= ele_text_length and not medias:  # content is empty if not text nor media
                return -1

            # retrieve receiver ID and target ID from data attributes (added by ourself) in HTML tag
            Rid = reply_ele.attrs["data-uid"]
            Tid = reply_ele.attrs["data-cid"]
            # if sender != receiver, send notification to comment owner
            if Uid != Rid:
                Notification.new("user", Uid, "user", Rid, "comment", Tid, "reply")

        # if sender != receiver, send notification to post owner
        if Uid != (Rid := match_post.owner.Uid):
            Notification.new("user", Uid, "user", Rid, "post", Pid, "comment")

        # record current available floor
        floor = match_post.availableFloor
        # update post statistics
        cls.update(cls.Pid == Pid, values={"availableFloor": floor + 1, "commentCount": match_post.commentCount,
                                           "latestCommentTime": datetime.datetime.utcnow()})
        return floor
