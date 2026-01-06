"""
Core caching utilities - re-exports from database.redis for backward compatibility.
"""
from app.database.redis import (
    RedisCache,
    redis_cache,
    init_redis_cache,
    close_redis_cache,
)

__all__ = [
    "RedisCache",
    "redis_cache",
    "init_redis_cache",
    "close_redis_cache",
]
