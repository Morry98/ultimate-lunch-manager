from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from ultimate_lunch_manager.config.config import Config

config = Config()

engine = create_engine(
    config.DB_CONN_STR,
    execution_options={"isolation_level": "AUTOCOMMIT"},
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=True,
    bind=engine,
)

Base = declarative_base()


# Dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
