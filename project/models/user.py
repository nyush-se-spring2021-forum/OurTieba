import datetime
import hashlib

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    __tablename__ = 'user'

    Uid = Column(Integer, primary_key=True)
    password = Column(String(200))
    uname = Column(String(50), unique=True)
    avatar = Column(String(100), default="")  # upon uploading, link=hash(Uid + timestamp) + ".png"
    timestamp = Column(DateTime, default=datetime.datetime.now())  # time of account creation

    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="comment_by")

    def __init__(self, password, uname, avatar=None, timestamp=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.password = hashlib.sha3_512(password.encode()).hexdigest()
        self.uname = uname
        self.avatar = avatar
        self.timestamp = timestamp

    def __repr__(self):
        return '<User %r>' % self.Uid
