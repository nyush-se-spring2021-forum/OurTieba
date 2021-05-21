import datetime
import hashlib
import time

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from ._tables import user_report_table
from .baseORM import BaseORM
from ..configs.macros import AVATAR_PATH
from ..database import my_db


class User(BaseORM, my_db.Base):
    """
    Mapping of table "user".
    """
    __tablename__ = 'user'

    Uid = Column(Integer, primary_key=True)
    password = Column(String)
    uname = Column(String, unique=True)
    nickname = Column(String, nullable=False)
    avatar = Column(String, default=AVATAR_PATH + "default_avatar.jpg")  # retrieved by hashing (Uid + upload timestamp)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)  # time of account creation
    lastCheck = Column(Integer, default=time.time)  # time the user last check message
    # personal info
    gender = Column(String)
    phoneNumber = Column(String)
    email = Column(String)
    address = Column(String)
    dateOfBirth = Column(DateTime)
    # ban status
    banned = Column(Integer, default=0)  # 0=False, 1=True
    banDuration = Column(DateTime, default=datetime.datetime.utcnow)  # banned until

    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="comment_by")
    reports = relationship("Report", secondary=lambda: user_report_table, back_populates="report_by")
    status_comment = relationship("CommentStatus", back_populates="by_user")
    status_post = relationship("PostStatus", back_populates="by_user")
    subscriptions = relationship("Subscription", back_populates="by_user")
    view = relationship('History', back_populates="by_user")

    def __init__(self, password, uname, nickname=None, avatar=None, timestamp=None, lastCheck=None, gender=None,
                 phone_number=None, email=None, address=None, dateOfBirth=None, banned=None, banDuration=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        if isinstance(dateOfBirth, str):
            dateOfBirth = datetime.datetime.strptime(dateOfBirth, "%Y-%m-%d %H:%M:%S")
        if isinstance(banDuration, str):
            banDuration = datetime.datetime.strptime(banDuration, "%Y-%m-%d %H:%M:%S")
        self.password = hashlib.sha3_512(password.encode()).hexdigest()
        self.uname = uname
        self.nickname = nickname if nickname else uname
        self.avatar = avatar
        self.timestamp = timestamp
        self.lastCheck = lastCheck
        self.gender = gender
        self.phoneNumber = phone_number
        self.email = email
        self.address = address
        self.dateOfBirth = dateOfBirth
        self.banned = banned
        self.banDuration = banDuration

    def __repr__(self):
        return '<User %r>' % self.Uid

    @classmethod
    def is_banned(cls, Uid):
        """
        Return whether user is banned or not. Will try to unban user before returning result.
        :param Uid: user ID.
        :return: 0 (not banned) or 1 (banned).
        """
        user = cls._get(Uid)
        if user.banDuration <= datetime.datetime.utcnow():
            user.banned = 0
        return user.banned

    @classmethod
    def get_info(cls, Uid):
        """
        Get a user's info by Uid. If user not exists, will return None.
        :param Uid: user ID.
        :return: None if user not exists, or user info dict
        """
        user = cls._get(Uid)
        if not user:
            return None
        user_info = {"Uid": Uid, "nickname": user.nickname, "avatar": user.avatar, "timestamp": user.timestamp,
                     "gender": user.gender, "phoneNumber": user.phoneNumber, "email": user.email,
                     "address": user.address, "dateOfBirth": user.dateOfBirth, "banned": user.banned,
                     "banDuration": str(user.banDuration)}
        return user_info

    @classmethod
    def ban(cls, Uid, days):
        """
        Ban a user by Uid for a given days. If user not exists, will return error message.
        :param Uid: user ID.
        :param days: the number of days to ban user for.
        :return: error message on failure, or success message on success.
        """
        user = cls._get(Uid)
        if not user:
            error = {"error": {"msg": "User not found."}, "status": 0}
            return error
        cls.update(User.Uid == Uid, values={"banned": 1,
                                            "banDuration": datetime.datetime.utcnow() + datetime.timedelta(
                                                days=int(days))})
        success = {'status': 1}
        return success

    @classmethod
    def unban(cls, Uid):
        """
        Unban a user by Uid. If user not exists, will return error message.
        :param Uid: user ID.
        :return: error message on failure, or success message on success.
        """
        user = cls._get(Uid)
        if not user:
            error = {"error": {"msg": "User not found."}, "status": 0}
            return error
        cls.update(User.Uid == Uid, values={"banned": 0, "banDuration": datetime.datetime.utcnow()})
        success = {'status': 1}
        return success

    @classmethod
    def add_personal_info(cls, Uid, values):
        """
        Update user's personal info with a given value dict.
        :param Uid: user ID.
        :param values: a dict of values to update.
        :return: nickname and avatar after update. (Note that they are not nullable)
        """
        cls.update(Uid, values=values)
        match_user = User._get(Uid)
        nickname = match_user.nickname
        avatar = match_user.avatar
        return nickname, avatar

    @classmethod
    def register_auth(cls, password, username, nickname):
        """
        Register a user with given info. If username already exists, will return failure (0).
        :param password: user's password in plaintext.
        :param username: user's username.
        :param nickname: user's nickname.
        :return: failure (0), or new user's info dict.
        """
        match_user = cls._query(cls.uname == username, first=True)
        if match_user:
            return 0
        cls.new(password, username, nickname)

        new_user = cls._query(cls.uname == username, first=True)
        user_info = {"Uid": new_user.Uid, "nickname": new_user.nickname, "avatar": new_user.avatar,
                     "last_check": new_user.lastCheck}
        return user_info

    @classmethod
    def login_auth(cls, username, password):
        match_user = cls._query(cls.uname == username, first=True)
        if not match_user:
            return 0
        if hashlib.sha3_512(password.encode()).hexdigest() != match_user.password:
            return 1
        user_info = {"Uid": match_user.Uid, "nickname": match_user.nickname, "avatar": match_user.avatar,
                     "last_check": match_user.lastCheck}
        return user_info

    @classmethod
    def get_avatar(cls, Uid):
        """
        Get the avatar of a user.
        :param Uid: user ID.
        :return: avatar of Uid.
        """
        return cls._get(Uid).avatar

    @classmethod
    def change_avatar(cls, Uid, new_avatar):
        """
        Update a user's avatar.
        :param Uid: user ID.
        :param new_avatar: new avatar path.
        :return: user's nickname and avatar after update.
        """
        cls.update(cls.Uid == Uid, values={"avatar": new_avatar})
        user = cls._get(Uid)
        return user.nickname, user.avatar

    @classmethod
    def get_post_info_list(cls, Uid):
        """
        Get info list of a user's posts.
        :param Uid: user ID.
        :return: user's post info list.
        """
        user = cls._get(Uid)
        post_info_list = [{"Pid": p.Pid, "Bid": p.Bid, "bname": p.under.name, "title": p.title,
                           "timestamp": p.timestamp, "status": p.status} for p in user.posts]
        return post_info_list

    @classmethod
    def get_comment_info_list(cls, Uid):
        """
        Get info list of a user's comments.
        :param Uid: user ID.
        :return: user's comment info list.
        """
        user = cls._get(Uid)
        comment_info_list = []
        for c in user.comments:
            comment = {"Cid": c.Cid, "text": c.text, "timestamp": c.timestamp, "status": c.status}
            p = c.comment_in
            comment.update({"Pid": p.Pid, "title": p.title})
            comment_info_list.append(comment)
        return comment_info_list

    @classmethod
    def get_subs_info_list(cls, Uid):
        """
        Get info list of a user's subscriptions.
        :param Uid: user ID.
        :return: user's subscription info list.
        """
        user = cls._get(Uid)
        subs_info_list = []
        for s in user.subscriptions:
            if s.subscribed == 1:
                if (b := s.of_board).status == 0:
                    subs_info_list.append({"Bid": s.Bid, "bname": b.name, "LM": s.lastModified,
                                           "cover": b.cover, "status": 0})
        return subs_info_list

    @classmethod
    def get_history_info_list(cls, Uid, cur_Uid):
        """
        Get info list of a user's history. If the post's owner in history is current user, will mark it as by "me".
        :param Uid: user ID.
        :param cur_Uid: ID of current user (user that starts this request).
        :return: user's history info list.
        """
        user = cls._get(Uid)
        history_info_list = []
        for h in user.view:
            history = {"Pid": h.Pid, "LVT": h.lastVisitTime}
            p = h.related_post
            history.update({"title": p.title, "bname": p.under.name, "Bid": p.Bid, "Uid": (u := p.owner).Uid,
                            "nickname": u.nickname, "me": int(u.Uid == cur_Uid),
                            "status": p.status})  # "me" = whether post by current user
            history_info_list.append(history)
        return history_info_list
