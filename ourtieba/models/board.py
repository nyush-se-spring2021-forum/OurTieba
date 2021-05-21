import datetime

from sqlalchemy import Column, Integer, String, DateTime, PickleType
from sqlalchemy.orm import relationship

from .baseORM import BaseORM
from .comment import Comment
from .post import Post
from ..database import my_db


class Board(BaseORM, my_db.Base):
    """
    Mapping of table "board". Note: "stickyOnTop" not implemented, "viewCount" not reflected on web page.
    """
    __tablename__ = "board"

    Bid = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    hot = Column(Integer, default=0)
    cover = Column(String, default="cover/OurTieba.png")
    status = Column(Integer, default=0)  # 0=normal, 1=deleted(by user), 2=banned(by admin)
    stickyOnTop = Column(PickleType, default=[])  # the list of Pid of post sticky on top
    postCount = Column(Integer, default=0)
    viewCount = Column(Integer, default=0)
    subscribeCount = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    posts = relationship("Post", back_populates="under")
    subscribers = relationship("Subscription", back_populates="of_board")

    def __init__(self, name, description, hot=None, cover=None, status=None, sticky_on_top=None, postCount=None,
                 viewCount=None, subscribeCount=None, timestamp=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.name = name
        self.description = description
        self.hot = hot
        self.cover = cover
        self.status = status
        self.stickyOnTop = sticky_on_top
        self.viewCount = viewCount
        self.subscribeCount = subscribeCount
        self.postCount = postCount
        self.timestamp = timestamp

    def __repr__(self):
        return "<Board %r>" % self.Bid

    @classmethod
    def action_on_post(cls, Bid, action):  # 0=add, 1=delete/ban
        """
        On post actions, modify post count of corresponding board. If board not found, return failure (0).
        :param Bid: board ID.
        :param action: 0 = add post, 1 = delete post.
        :return: failure (0) or success (1).
        """
        board = cls._get(Bid)
        if not board:
            return 0  # board not exists, unsuccessful
        board.postCount += 1 if action == 0 else -1
        return 1

    @classmethod
    def name_exists(cls, name):
        """
        Whether board name already exists or not.
        :param name: board name to check.
        :return: True if exists else False.
        """
        return cls.query_exists(cls.name == name)

    @classmethod
    def get_recommend(cls, num):
        """
        Get info list of certain number of recommended boards.
        :param num: number of recommended boards.
        :return: recommended boards info list.
        """
        boards = cls._query(order=Board.hot.desc(), limit=num)
        boards_info_list = [{"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount, "cover": b.cover}
                            for b in boards]
        return boards_info_list

    @classmethod
    def ban_board(cls, Bid):
        """
        Ban a board by Bid. Will also ban all posts and comments under it. If board not exists, will return error.
        :param Bid: board ID.
        :return: error message on failure, or success message on success.
        """
        match_board = cls._get(Bid)
        if not match_board:
            error = {"error": {"msg": "Board not found."}, "status": 0}
            return error

        match_board.postCount -= 1
        cls._ban(cls.Bid == Bid)
        for p in match_board.posts:
            for c in p.comments:
                Comment._ban(Comment.Cid == c.Cid)
            Post._ban(Post.Pid == p.Pid)
        success = {'status': 1}
        return success

    @classmethod
    def restore_board(cls, Bid, by):
        """
        Restore a board by Bid. Will also restore all posts and comments under it (unless deleted by user).
        If board not exists, will return error.
        :param by: who starts this action. "user" or "admin".
        :param Bid: board ID.
        :return: error message on failure, or success message on success.
        """
        match_board = cls._get(Bid)
        if not match_board:
            error = {"error": {"msg": "Board not found."}, "status": 0}
            return error

        match_board.postCount += 1
        cls._restore(cls.Bid == Bid, by="admin")
        for p in match_board.posts:
            for c in p.comments:
                Comment._restore(Comment.Cid == c.Cid, by=by)
            Post._restore(Post.Pid == p.Pid, by=by)
        success = {'status': 1}
        return success

    @classmethod
    def get_info(cls, Bid, increment_view=False):
        """
        Get board info by Bid, also increment view count if specified. If board not exists, will return None.
        :param Bid: board ID.
        :param increment_view: whether to increment view count.
        :return: board info dict.
        """
        board = cls._get(Bid)
        if not board:
            return None  # board not exists, unsuccessful
        if increment_view:
            board.viewCount += 1
        board_info = {"Bid": board.Bid, "name": board.name, "hot": board.hot, "post_count": board.postCount,
                      "subs_count": board.subscribeCount, "time": board.timestamp, "view_count": board.viewCount,
                      "cover": board.cover, "description": board.description}
        return board_info

    @classmethod
    def get_search_count(cls, keyword):
        """
        Get number of search results by keyword.
        :param keyword: keyword to search.
        :return: count of search results.
        """
        search_count = cls.count(Board.name.like("%" + keyword + "%"))
        return search_count

    @classmethod
    def get_search_list_by_page(cls, page_num, page_size, keyword, order):
        """
        Get board info list by searching keyword and pagination.
        :param page_num: indicates from which page to fetch.
        :param page_size: how many results on one page.
        :param keyword: keyword to search.
        :param order: by what order the results are sorted.
        :return: board info list.
        """
        boards = cls._query(Board.name.like("%" + keyword + "%"), order=order, limit=page_size,
                            offset=(page_num - 1) * page_size)
        board_search_list = [{"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount} for b in boards]
        return board_search_list

    @classmethod
    def action_on_subs(cls, Bid, update):
        """
        On subscribe action, modify board's subscribe count.
        :param Bid: board ID.
        :param update: 1 (subscribe) or -1 (unsubscribe).
        :return: subscribe count after update.
        """
        board = cls._get(Bid)
        board.subscribeCount += update
        return board.subscribeCount
