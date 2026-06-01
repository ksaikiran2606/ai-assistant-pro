"""Database engine and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings
from app.db_utils import build_mysql_connect_args

settings = get_settings()

_engine_kwargs: dict = {
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
}

if settings.database_url.startswith("mysql"):
    _engine_kwargs["connect_args"] = build_mysql_connect_args(
        settings.database_url,
        settings.mysql_ssl_ca,
        settings.mysql_ssl_ca_file,
        settings.mysql_ssl_insecure,
    )

engine = create_engine(settings.database_url, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
