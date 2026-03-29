"""
Redis Cache Service

Provides caching layer for API responses to improve performance.
Cache-aside pattern with automatic serialization.
"""
import json
import hashlib
from typing import Optional, Any, Callable, TypeVar, ParamSpec
from functools import wraps
import logging

from redis import asyncio as aioredis
from pydantic import BaseModel

from core.config import settings

logger = logging.getLogger(__name__)

# Type variables for generic decorator
P = ParamSpec("P")
T = TypeVar("T")


class CacheService:
    """
    Redis cache service with automatic serialization

    Features:
    - Async operations
    - Automatic JSON serialization
    - TTL support
    - Cache-aside pattern
    - Decorator for easy caching

    Usage:
        cache = CacheService()

        # Direct usage
        data = await cache.get_or_set("key", fetch_func, ttl=300)

        # Decorator usage
        @cache.cached("prefix", ttl=300)
        async def get_data():
            return {"data": "value"}
    """

    def __init__(self, redis_url: str = None):
        """
        Initialize cache service

        Args:
            redis_url: Redis connection URL (default from settings)
        """
        self.redis_url = redis_url or settings.REDIS_URL
        self._redis: Optional[aioredis.Redis] = None

        # Default TTL values (in seconds)
        self.default_ttl = 300  # 5 minutes
        self.ttl_config = {
            "contents_list": 300,        # 5 minutes
            "content_detail": 3600,      # 1 hour
            "popular": 900,              # 15 minutes
            "category": 600,             # 10 minutes
            "search": 300,               # 5 minutes
            "related": 600,              # 10 minutes
        }

    async def _get_redis(self) -> aioredis.Redis:
        """Get or create Redis connection"""
        if self._redis is None:
            self._redis = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis

    async def close(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from prefix and arguments

        Args:
            prefix: Key prefix (e.g., "contents", "search")
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Cache key string
        """
        # Create a string representation of arguments
        key_parts = [prefix]

        for arg in args:
            if isinstance(arg, BaseModel):
                key_parts.append(arg.model_dump_json())
            elif isinstance(arg, (dict, list)):
                key_parts.append(json.dumps(arg, sort_keys=True))
            else:
                key_parts.append(str(arg))

        for k, v in sorted(kwargs.items()):
            if isinstance(v, BaseModel):
                key_parts.append(f"{k}:{v.model_dump_json()}")
            elif isinstance(v, (dict, list)):
                key_parts.append(f"{k}:{json.dumps(v, sort_keys=True)}")
            else:
                key_parts.append(f"{k}:{v}")

        # Hash if key is too long
        full_key = ":".join(key_parts)
        if len(full_key) > 200:
            hash_suffix = hashlib.md5(full_key.encode()).hexdigest()[:16]
            return f"{prefix}:hash:{hash_suffix}"

        return full_key

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            redis = await self._get_redis()
            data = await redis.get(key)

            if data is None:
                logger.debug(f"Cache miss: {key}")
                return None

            logger.debug(f"Cache hit: {key}")
            return json.loads(data)

        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default from config)

        Returns:
            True if successful, False otherwise
        """
        try:
            redis = await self._get_redis()
            ttl = ttl or self.default_ttl

            # Serialize value
            if isinstance(value, BaseModel):
                data = value.model_dump_json()
            else:
                data = json.dumps(value)

            await redis.setex(key, ttl, data)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        try:
            redis = await self._get_redis()
            result = await redis.delete(key)
            return result > 0

        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern

        Args:
            pattern: Key pattern (e.g., "contents:*")

        Returns:
            Number of keys deleted
        """
        try:
            redis = await self._get_redis()
            keys = await redis.keys(pattern)

            if keys:
                result = await redis.delete(*keys)
                logger.info(f"Deleted {result} keys matching '{pattern}'")
                return result

            return 0

        except Exception as e:
            logger.error(f"Cache delete_pattern error for '{pattern}': {e}")
            return 0

    async def get_or_set(
        self,
        key: str,
        fetch_func: Callable[[], T],
        ttl: int = None
    ) -> T:
        """
        Get from cache, or fetch and cache the result

        Cache-aside pattern implementation

        Args:
            key: Cache key
            fetch_func: Async function to fetch data if not cached
            ttl: Time to live in seconds

        Returns:
            Cached or fetched data
        """
        # Try to get from cache
        cached = await self.get(key)
        if cached is not None:
            return cached

        # Fetch fresh data
        import asyncio
        if asyncio.iscoroutinefunction(fetch_func):
            data = await fetch_func()
        else:
            data = fetch_func()

        # Cache the result
        await self.set(key, data, ttl)

        return data

    def cached(self, prefix: str, ttl: int = None):
        """
        Decorator for caching function results

        Usage:
            @cache.cached("contents", ttl=300)
            async def get_contents(page: int, size: int):
                return await db.query(...)

        Args:
            prefix: Cache key prefix
            ttl: Time to live in seconds

        Returns:
            Decorated function
        """
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                # Generate cache key
                key = self._generate_key(prefix, *args, **kwargs)

                # Try cache first
                cached = await self.get(key)
                if cached is not None:
                    return cached

                # Call original function
                result = await func(*args, **kwargs)

                # Cache result
                await self.set(key, result, ttl)

                return result

            return wrapper

        return decorator

    async def incr(self, key: str) -> int:
        """
        Increment counter in cache

        Args:
            key: Counter key

        Returns:
            New value after increment
        """
        try:
            redis = await self._get_redis()
            return await redis.incr(key)

        except Exception as e:
            logger.error(f"Cache incr error for key '{key}': {e}")
            return 0

    async def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        try:
            redis = await self._get_redis()
            info = await redis.info()

            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }

        except Exception as e:
            logger.error(f"Cache get_stats error: {e}")
            return {}

    def _calculate_hit_rate(self, hits: int, misses: int) -> str:
        """Calculate cache hit rate"""
        total = hits + misses
        if total == 0:
            return "0%"
        rate = (hits / total) * 100
        return f"{rate:.1f}%"


# Global cache instance
cache = CacheService()


async def get_cache() -> CacheService:
    """Dependency for getting cache service"""
    return cache
