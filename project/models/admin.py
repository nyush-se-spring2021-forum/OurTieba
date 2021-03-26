import datetime
import hashlib

from sqlalchemy import Column, Integer, String, DateTime

from ..database import Base


class Admin(Base):
    __tablename__ = 'admin'

    Aid = Column(Integer, primary_key=True)
    password = Column(String(200))
    aname = Column(String(50), unique=True)
    avatar = Column(String(100), default="")  # upon uploading, link=hash(Aid + timestamp) + ".png"
    timestamp = Column(DateTime, default=datetime.datetime.now().replace(microsecond=0))  # time of account creation

    def __init__(self, password, aname=None, avatar=None, timestamp=None):
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.password = hashlib.sha3_512(password.encode()).hexdigest()
        self.aname = aname if aname else "admin" + str(self.Aid)
        self.avatar = avatar
        self.timestamp = timestamp

    def __repr__(self):
        return '<Admin %r>' % self.Aid