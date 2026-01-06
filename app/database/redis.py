"""
Redis async client for caching and session management.
"""
import json
import logging
from typing import Optional, Any, Dict, List
from urllib.parse import urlparse

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Async Redis cache client."""
    
    def __init__(self):
        """Initialize Redis cache client."""
        self.redis: Optional[Redis] = None
        self._connected = False
    
    async def connect(self) -> None:
        """
        Connect to Redis server.
        
        Raises:
            Exception: If connection fails
        """
        if self._connected and self.redis:
            return
        
        try:
            redis_url = settings.redis_connection_url
            if not redis_url:
                logger.warning("Redis URL not configured, caching will be disabled")
                return
            
            # Parse URL and create connection
            parsed = urlparse(redis_url)
            
            # Extract connection parameters
            host = parsed.hostname or settings.REDIS_HOST
            port = parsed.port or settings.REDIS_PORT
            db = int(parsed.path.lstrip('/')) if parsed.path else settings.REDIS_DB
            password = parsed.password or settings.REDIS_PASSWORD
            
            # Create Redis connection
            self.redis = await aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis.ping()
            self._connected = True
            logger.info(f"Connected to Redis at {host}:{port}/{db}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._connected = False
            self.redis = None
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Redis server."""
        if self.redis:
            try:
                await self.redis.aclose()
            except Exception as e:
                logger.error(f"Error disconnecting from Redis: {e}")
            finally:
                self.redis = None
                self._connected = False
    
    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        return self._connected and self.redis is not None
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.is_connected():
            return None
        
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
            
        Returns:
            True if successful
        """
        if not self.is_connected():
            return False
        
        try:
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value)
            else:
                serialized = str(value)
            
            if ttl:
                await self.redis.setex(key, ttl, serialized)
            else:
                await self.redis.set(key, serialized)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful
        """
        if not self.is_connected():
            return False
        
        try:
            result = await self.redis.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis DELETE error for key '{key}': {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "auth:user:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.is_connected():
            return 0
        
        try:
            count = 0
            async for key in self.redis.scan_iter(match=pattern):
                await self.redis.delete(key)
                count += 1
            return count
        except Exception as e:
            logger.error(f"Redis DELETE_PATTERN error for pattern '{pattern}': {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists
        """
        if not self.is_connected():
            return False
        
        try:
            result = await self.redis.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis EXISTS error for key '{key}': {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration on key.
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        if not self.is_connected():
            return False
        
        try:
            return await self.redis.expire(key, ttl)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key '{key}': {e}")
            return False
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for key.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds, -1 if no expiration, None if key doesn't exist
        """
        if not self.is_connected():
            return None
        
        try:
            ttl = await self.redis.ttl(key)
            return ttl
        except Exception as e:
            logger.error(f"Redis TTL error for key '{key}': {e}")
            return None


# Global Redis cache instance
redis_cache = RedisCache()


# Lifecycle functions for FastAPI
async def init_redis_cache():
    """Initialize Redis cache on application startup."""
    try:
        await redis_cache.connect()
    except Exception as e:
        logger.warning(f"Redis initialization failed: {e}. Caching will be disabled.")


async def close_redis_cache():
    """Close Redis cache on application shutdown."""
    await redis_cache.disconnect()

