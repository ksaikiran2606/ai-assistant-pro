"""Alembic migration environment."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

from app.config import get_settings
from app.database import Base
from app.db_utils import build_mysql_connect_args
from app.models import Chat, Message, User  # noqa: F401

config = context.config
settings = get_settings()

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _engine_connect_args() -> dict:
    if settings.database_url.startswith("mysql"):
        return build_mysql_connect_args(
            settings.database_url,
            settings.mysql_ssl_ca,
            settings.mysql_ssl_ca_file,
            settings.mysql_ssl_insecure,
        )
    return {}


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine

    connectable = create_engine(
        settings.database_url,
        poolclass=pool.NullPool,
        connect_args=_engine_connect_args(),
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
