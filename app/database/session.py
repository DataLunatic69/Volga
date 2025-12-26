"""Database session factory."""
from sqlmodel import SQLModel
from typing import AsyncGenerator
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Import all models so SQLModel can create tables
# This ensures all table metadata is registered with SQLModel
try:
    # Try relative import first (when imported as a module)
    from .models import *  # noqa: F401, F403
except ImportError:
    # Fallback for when running as a script
    import sys
    from pathlib import Path
    # Add the ai-backend directory to Python path
    backend_dir = Path(__file__).parent.parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    from app.database.models import *  # noqa: F401, F403

# URL encode the password: @ becomes %40
# Original: postgresql+asyncpg://postgres:Aura@123@db.qwddxnvcdkubctgkqtpa.supabase.co:5432/postgres
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:Aura%40123@db.qwddxnvcdkubctgkqtpa.supabase.co:5432/postgres"
)

# Create async engine
async_engine = create_async_engine(
    url=DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Connection pool size
    max_overflow=10  # Max connections beyond pool_size
)


async def create_db_and_tables():
    """Create all database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database dependency for FastAPI.
    
    Yields:
        Database session.
    """
    async_session = async_sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(create_db_and_tables())