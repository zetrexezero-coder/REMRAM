from SaitamaRobot import DB_URI
from sqlalchemy import BigInteger, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


def start() -> scoped_session:
    kwargs = {} if DB_URI.startswith("sqlite") else {"client_encoding": "utf8"}
    engine = create_engine(DB_URI, **kwargs)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


BASE = declarative_base()
SESSION = start()
