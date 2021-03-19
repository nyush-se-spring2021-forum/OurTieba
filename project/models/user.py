from sqlalchemy import Column, String
from ..database import Base
import hashlib


class User(Base):
    __tablename__ = 'user'

    Uid = Column(String(20), primary_key=True)
    password = Column(String(200))

    def __init__(self, Uid=None, password=None):
        self.Uid = Uid
        self.password = hashlib.sha3_512(password.encode()).hexdigest()

    def __repr__(self):
        return '<User %r>' % self.Uid
