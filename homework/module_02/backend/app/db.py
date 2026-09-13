"""SQLAlchemy engine/session setup.

Uses SQLite so the whole stack still runs with zero external services;
swapping to Postgres later is a `DATABASE_URL` change, not a rewrite,
since nothing above this module talks SQL directly.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def make_session_factory(database_url: str) -> sessionmaker[Session]:
    is_sqlite = database_url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    poolclass = StaticPool if database_url == "sqlite:///:memory:" else None

    engine = create_engine(
        database_url,
        connect_args=connect_args,
        **({"poolclass": poolclass} if poolclass else {}),
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
