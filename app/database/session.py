"""Database session factory."""
from sqlmodel import SQLModel
from typing import AsyncGenerator
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


try:

    from .models import *  # noqa: F401, F403
except ImportError:
   
    import sys
    from pathlib import Path
   
    backend_dir = Path(__file__).parent.parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    from app.database.models import *  # noqa: F401, F403


DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres.qwddxnvcdkubctgkqtpa:Aura%40123@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

)

# Create async engine
async_engine = create_async_engine(
    url=DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=15,  # Connection pool size
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