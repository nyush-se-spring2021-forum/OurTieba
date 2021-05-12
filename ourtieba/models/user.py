import datetime
import hashlib
import time

from sqlalchemy import Column, Integer, String, DateTime, DECIMAL
from sqlalchemy.orm import relationship

from ..configs.macros import AVATAR_PATH
from ._tables import user_report_table
from ..database import my_db


class User(my_db.Base):
    __tablename__ = 'user'

    Uid = Column(Integer, primary_key=True)
    password = Column(String)
    uname = Column(String, unique=True)
    nickname = Column(String)
    avatar = Column(String, default=AVATAR_PATH+"default_avatar.jpg")  # retrieved by hashing (Uid + upload timestamp)
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
