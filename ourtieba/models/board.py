import datetime

from sqlalchemy import Column, Integer, String, DateTime, PickleType
from sqlalchemy.orm import relationship

from .baseORM import BaseORM
from ..database import my_db


class Board(BaseORM, my_db.Base):
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
        board = cls._get(Bid)
        if not board:
            return 0  # board not exists, unsuccessful
        board.postCount += 1 if action == 0 else -1
        return 1

    @classmethod
    def name_exists(cls, name):
        return cls.query_exists(cls.name == name)

    @classmethod
    def get_recommend(cls, num):
        boards = cls._query(order=Board.hot.desc(), limit=num)
        boards_info_list = [{"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount, "cover": b.cover}
                            for b in boards]
        return boards_info_list

    @classmethod
    def get_info(cls, Bid, increment_view=False):
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
        search_count = cls.count(Board.name.like("%" + keyword + "%"))
        return search_count

    @classmethod
    def get_search_list_by_page(cls, page_num, page_size, keyword, order):
        boards = cls._query(Board.name.like("%" + keyword + "%"), order=order, limit=page_size,
                            offset=(page_num-1)*page_size)
        board_search_list = [{"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount} for b in boards]
        return board_search_list
