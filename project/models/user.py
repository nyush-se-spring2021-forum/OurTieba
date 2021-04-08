import datetime
import hashlib

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from ._tables import user_report_table
from ..database import my_db


class User(my_db.Base):
    __tablename__ = 'user'

    Uid = Column(Integer, primary_key=True)
    password = Column(String)
    uname = Column(String, unique=True)
    nickname = Column(String)
    avatar = Column(String, default="default_avatar.jpg")  # upon uploading, link=hash(Uid + timestamp) + ".png"
    timestamp = Column(DateTime, default=datetime.datetime.now())  # time of account creation
    # personal info
    gender = Column(String)
    phoneNumber = Column(String)
    email = Column(String)
    address = Column(String)
    dateOfBirth = Column(DateTime)
    # ban status
    banned = Column(Integer, default=0)  # 0=False, 1=True
    banDuration = Column(DateTime, default=datetime.datetime.now())  # banned until

    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="comment_by")
    reports = relationship("Report", secondary=lambda: user_report_table, back_populates="report_by")
    status_comment = relationship("CommentStatus", back_populates="by_user")
    status_post = relationship("PostStatus", back_populates="by_user")
    subscriptions = relationship("Subscription", back_populates="by_user")

    def __init__(self, password, uname, nickname=None, avatar=None, timestamp=None, gender=None,
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
        self.gender = gender
        self.phoneNumber = phone_number
        self.email = email
        self.address = address
        self.dateOfBirth = dateOfBirth
        self.banned = banned
        self.banDuration = banDuration

    def __repr__(self):
        return '<User %r>' % self.Uid
