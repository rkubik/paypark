# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, create_session
from sqlalchemy.ext.declarative import declarative_base


engine = None
db_session = scoped_session(
    lambda: create_session(
        autocommit=False,
        autoflush=True,
        bind=engine
    )
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_engine(uri, **kwargs):
    global engine
    engine = create_engine(uri, **kwargs)
    return engine


def init_db():
    import paypark.models
    Base.metadata.create_all(bind=engine)
