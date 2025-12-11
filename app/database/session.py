"""Database session factory."""
from sqlmodel import SQLModel
from typing import AsyncGenerator
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://nexcell_user:MeJJ02CeEVzga1C7GS4wA59ZQEj4bq5P@dpg-d4sna6k9c44c73eqgca0-a/nexcell"
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