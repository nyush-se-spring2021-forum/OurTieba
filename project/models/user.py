from sqlalchemy import Column, Integer, String, DateTime
from ..database import Base
import hashlib
import datetime


class User(Base):
    __tablename__ = 'user'

    Uid = Column(Integer, primary_key=True)
    password = Column(String(200))
    uname = Column(String(50), unique=True)
    timestamp = Column(DateTime, default=datetime.datetime.now())  # time of account creation

    def __init__(self, password, uname, timestamp=None):
        self.password = hashlib.sha3_512(password.encode()).hexdigest()
        self.uname = uname
        self.timestamp = timestamp

    def __repr__(self):
        return '<User %r>' % self.Uid
