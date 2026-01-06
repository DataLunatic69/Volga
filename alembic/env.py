from logging.config import fileConfig
import os
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import your SQLModel base and all models
from sqlmodel import SQLModel

# Clear any existing metadata to avoid conflicts
SQLModel.metadata.clear()

# Try to import models, but continue even if there's an error
# This allows migrations to run even if models have issues
try:
    from app.database.models import *  # This imports all your models
except Exception as e:
    # Log the error but continue - migrations can still run
    import warnings
    warnings.warn(f"Could not import all models: {e}. Migration may proceed anyway.")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override the sqlalchemy.url from environment variable if present
database_url = os.getenv(
    "DATABASE_URL",
    # Use the pooler endpoint which supports IPv4
    "postgresql+asyncpg://postgres.qwddxnvcdkubctgkqtpa:Aura%40123@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"
)

# Alembic needs psycopg2, not asyncpg
database_url = database_url.replace("+asyncpg", "")

# Escape % characters for configparser by doubling them
database_url = database_url.replace("%", "%%")

config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata to SQLModel's metadata
target_metadata = SQLModel.metadata


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