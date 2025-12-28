# Alembic Configuration

# This is the Alembic configuration object
# For more information, visit: https://alembic.sqlalchemy.org/

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

# Add app to path
sys.path.insert(0, os.path.dirname(__file__).replace('/alembic', ''))

from app.config import get_settings
from app.models import Base

# this is the Alembic Config object
config = fileConfig(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))

# set the sqlalchemy.url from .env
settings = get_settings()
config.set_main_option('sqlalchemy.url', settings.database_url)

# Adds support for unicode for autogenerate's --unicode arguments
# config.add_task_handler('sqlalchemy.url', settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
