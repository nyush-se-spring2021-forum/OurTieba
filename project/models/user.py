import datetime
import hashlib

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    __tablename__ = 'user'

    Uid = Column(Integer, primary_key=True)
    password = Column(String)
    uname = Column(String, unique=True)
    nickname = Column(String)
    avatar = Column(String)  # upon uploading, link=hash(Uid + timestamp) + ".png"
    timestamp = Column(DateTime, default=datetime.datetime.now())  # time of account creation
    # personal info
    gender = Column(String)
    phoneNumber = Column(String)
    email = Column(String)
    address = Column(String)
    dateOfBirth = Column(DateTime)

    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="comment_by")

    def __init__(self, password, uname, nickname=None, avatar=None, timestamp=None, gender=None,
                 phoneNumber=None, email=None, address=None, dateOfBirth=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.password = hashlib.sha3_512(password.encode()).hexdigest()
        self.uname = uname
        self.nickname = nickname if nickname else uname
        self.avatar = avatar
        self.timestamp = timestamp
        self.gender = gender
        self.phoneNumber = phoneNumber
        self.email = email
        self.address = address
        self.dateOfBirth = dateOfBirth

    def __repr__(self):
        return '<User %r>' % self.Uid
