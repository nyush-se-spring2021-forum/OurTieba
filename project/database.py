from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///test.db', convert_unicode=True)
DB_session = scoped_session(sessionmaker(autocommit=True,
                                         bind=engine))
db_session = DB_session()

Base = declarative_base()
Base.query = DB_session.query_property()


def init_db():
    # import all models here (only the class name)
    from .models import User, Post
    Base.metadata.create_all(bind=engine)
