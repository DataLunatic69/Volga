"""
Rate Limiting - Redis-based rate limiter for API endpoints.

Implements sliding window rate limiting with different limits for:
- Authentication endpoints (stricter)
- General API endpoints (relaxed)
- Per-user limits
- Per-IP limits

Uses Redis for distributed rate limiting across multiple workers.
"""
from typing import Optional, Tuple
import time
import logging
from dataclasses import dataclass

from app.core.cache import redis_cache

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests: int  # Max requests
    window_seconds: int  # Time window
    
    def __str__(self) -> str:
        return f"{self.requests}/{self.window_seconds}s"


# Rate limit configurations for different endpoint types
class RateLimits:
    """Predefined rate limit configurations."""
    
    # Auth endpoints - stricter limits
    LOGIN = RateLimitConfig(requests=5, window_seconds=60)  # 5/min
    REGISTER = RateLimitConfig(requests=3, window_seconds=60)  # 3/min
    FORGOT_PASSWORD = RateLimitConfig(requests=3, window_seconds=300)  # 3/5min
    RESET_PASSWORD = RateLimitConfig(requests=5, window_seconds=300)  # 5/5min
    VERIFY_EMAIL = RateLimitConfig(requests=10, window_seconds=60)  # 10/min
    REFRESH_TOKEN = RateLimitConfig(requests=10, window_seconds=60)  # 10/min
    
    # General API - relaxed limits
    API_DEFAULT = RateLimitConfig(requests=100, window_seconds=60)  # 100/min
    API_WRITE = RateLimitConfig(requests=30, window_seconds=60)  # 30/min
    API_SEARCH = RateLimitConfig(requests=50, window_seconds=60)  # 50/min
    
    # Per-user vs per-IP multipliers
    USER_MULTIPLIER = 2  # Authenticated users get 2x limit


class RateLimiter:
    """
    Redis-based sliding window rate limiter.
    
    Uses sorted sets for efficient sliding window counting.
    """
    
    KEY_PREFIX = "ratelimit"
    
    @classmethod
    async def check_rate_limit(
        cls,
        identifier: str,
        limit_type: str,
        config: RateLimitConfig,
        is_authenticated: bool = False
    ) -> Tuple[bool, int, int]:
        """
        Check if request is within rate limit.
        
        Args:
            identifier: Unique identifier (IP or user_id)
            limit_type: Type of limit (e.g., "login", "api")
            config: Rate limit configuration
            is_authenticated: If True, apply user multiplier
            
        Returns:
            Tuple of (allowed, remaining, reset_after_seconds)
        """
        if not redis_cache.is_connected() or not redis_cache.redis:
            # Redis not available - allow all requests
            logger.warning("Rate limiter: Redis not available, allowing request")
            return True, config.requests, config.window_seconds
        
        # Calculate effective limit
        max_requests = config.requests
        if is_authenticated:
            max_requests = int(max_requests * RateLimits.USER_MULTIPLIER)
        
        # Build key
        key = f"{cls.KEY_PREFIX}:{limit_type}:{identifier}"
        now = time.time()
        window_start = now - config.window_seconds
        
        try:
            redis_client = redis_cache.redis
            
            # Use pipeline for atomic operations
            pipe = redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            pipe.zcard(key)
            
            # Execute pipeline
            results = await pipe.execute()
            current_count = results[1]
            
            if current_count >= max_requests:
                # Rate limit exceeded
                # Get oldest entry to calculate reset time
                oldest = await redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    reset_after = int(oldest[0][1] + config.window_seconds - now)
                else:
                    reset_after = config.window_seconds
                
                remaining = 0
                logger.warning(
                    f"Rate limit exceeded: {identifier} for {limit_type} "
                    f"({current_count}/{max_requests})"
                )
                return False, remaining, max(1, reset_after)
            
            # Add current request
            await redis_client.zadd(key, {str(now): now})
            
            # Set TTL on key
            await redis_client.expire(key, config.window_seconds + 60)
            
            remaining = max_requests - current_count - 1
            return True, remaining, config.window_seconds
            
        except Exception as e:
            logger.error(f"Rate limiter error: {e}", exc_info=True)
            # On error, allow the request
            return True, config.requests, config.window_seconds
    
    @classmethod
    async def get_rate_limit_headers(
        cls,
        config: RateLimitConfig,
        remaining: int,
        reset_after: int
    ) -> dict:
        """
        Generate rate limit headers.
        
        Args:
            config: Rate limit configuration
            remaining: Remaining requests
            reset_after: Seconds until reset
            
        Returns:
            Dict of rate limit headers
        """
        return {
            "X-RateLimit-Limit": str(config.requests),
            "X-RateLimit-Remaining": str(max(0, remaining)),
            "X-RateLimit-Reset": str(reset_after),
        }
    
    @classmethod
    async def reset_rate_limit(cls, identifier: str, limit_type: str) -> None:
        """
        Reset rate limit for an identifier.
        
        Useful after successful login to reset failed attempt counter.
        
        Args:
            identifier: Unique identifier (IP or user_id)
            limit_type: Type of limit
        """
        if not redis_cache.is_connected() or not redis_cache.redis:
            return
        
        key = f"{cls.KEY_PREFIX}:{limit_type}:{identifier}"
        try:
            await redis_cache.redis.delete(key)
        except Exception as e:
            logger.error(f"Failed to reset rate limit: {e}")


# Endpoint to rate limit config mapping
ENDPOINT_RATE_LIMITS = {
    "/api/v1/login": RateLimits.LOGIN,
    "/api/v1/register": RateLimits.REGISTER,
    "/api/v1/forgot-password": RateLimits.FORGOT_PASSWORD,
    "/api/v1/reset-password": RateLimits.RESET_PASSWORD,
    "/api/v1/verify-email": RateLimits.VERIFY_EMAIL,
    "/api/v1/resend-verification": RateLimits.VERIFY_EMAIL,
    "/api/v1/refresh": RateLimits.REFRESH_TOKEN,
}


def get_rate_limit_for_path(path: str, method: str = "GET") -> RateLimitConfig:
    """
    Get rate limit config for a path.
    
    Args:
        path: Request path
        method: HTTP method
        
    Returns:
        Rate limit configuration
    """
    # Check exact matches first
    if path in ENDPOINT_RATE_LIMITS:
        return ENDPOINT_RATE_LIMITS[path]
    
    # Write operations get stricter limits
    if method in ("POST", "PUT", "PATCH", "DELETE"):
        return RateLimits.API_WRITE
    
    # Default API limit
    return RateLimits.API_DEFAULT

