import datetime
import hashlib

from sqlalchemy import Column, Integer, String, DateTime

from ..database import my_db


class Admin(my_db.Base):
    __tablename__ = 'admin'

    Aid = Column(Integer, primary_key=True)
    password = Column(String)
    aname = Column(String, unique=True)
    nickname = Column(String)
    avatar = Column(String, default="avatar/default_avatar.jpg")  # upon uploading, link=hash(Aid + timestamp) + ".png"
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)  # time of account creation

    def __init__(self, password, aname=None, nickname=None, avatar=None, timestamp=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.password = hashlib.sha3_512(password.encode()).hexdigest()
        self.aname = aname if aname else "admin" + str(hash(datetime.datetime.utcnow))
        self.nickname = nickname if nickname else self.aname
        self.avatar = avatar
        self.timestamp = timestamp

    def __repr__(self):
        return '<Admin %r>' % self.Aid