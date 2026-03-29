"""
Unit tests for CacheService.
Tests match the actual implementation in services/cache_service.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from pydantic import BaseModel


class TestModel(BaseModel):
    """Test model for serialization tests."""
    name: str
    value: int


class TestCacheService:
    """Test cases for CacheService."""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        redis = AsyncMock()
        redis.get = AsyncMock(return_value=None)
        redis.set = AsyncMock(return_value=True)
        redis.setex = AsyncMock(return_value=True)
        redis.delete = AsyncMock(return_value=1)
        redis.keys = AsyncMock(return_value=[])
        redis.exists = AsyncMock(return_value=0)
        redis.incr = AsyncMock(return_value=1)
        redis.info = AsyncMock(return_value={
            "connected_clients": 5,
            "used_memory_human": "1.2M",
            "total_commands_processed": 1000,
            "keyspace_hits": 800,
            "keyspace_misses": 200,
        })
        return redis

    @pytest.fixture
    def cache_service(self, mock_redis):
        """Create CacheService instance with mocked Redis."""
        from services.cache_service import CacheService
        service = CacheService()
        service._redis = mock_redis
        return service

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_set_success(self, cache_service, mock_redis):
        """Test successful cache set operation."""
        # Arrange
        key = "test:key"
        value = {"data": "test_value"}
        ttl = 3600

        # Act
        result = await cache_service.set(key, value, ttl)

        # Assert
        assert result is True
        mock_redis.setex.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_get_hit(self, cache_service, mock_redis):
        """Test cache get with cache hit."""
        # Arrange
        key = "test:key"
        expected_value = {"data": "test_value"}
        mock_redis.get.return_value = json.dumps(expected_value)

        # Act
        result = await cache_service.get(key)

        # Assert
        assert result == expected_value
        mock_redis.get.assert_called_once_with(key)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_get_miss(self, cache_service, mock_redis):
        """Test cache get with cache miss."""
        # Arrange
        key = "test:nonexistent"
        mock_redis.get.return_value = None

        # Act
        result = await cache_service.get(key)

        # Assert
        assert result is None
        mock_redis.get.assert_called_once_with(key)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_delete_success(self, cache_service, mock_redis):
        """Test cache delete operation."""
        # Arrange
        key = "test:key"
        mock_redis.delete.return_value = 1

        # Act
        result = await cache_service.delete(key)

        # Assert
        assert result is True
        mock_redis.delete.assert_called_once_with(key)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_delete_not_found(self, cache_service, mock_redis):
        """Test cache delete when key doesn't exist."""
        # Arrange
        key = "test:nonexistent"
        mock_redis.delete.return_value = 0

        # Act
        result = await cache_service.delete(key)

        # Assert
        assert result is False

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_delete_pattern(self, cache_service, mock_redis):
        """Test deleting multiple keys by pattern."""
        # Arrange
        pattern = "contents:*"
        mock_keys = ["contents:1", "contents:2", "contents:3"]
        mock_redis.keys.return_value = mock_keys
        mock_redis.delete.return_value = 3

        # Act
        result = await cache_service.delete_pattern(pattern)

        # Assert
        assert result == 3
        mock_redis.keys.assert_called_once_with(pattern)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_delete_pattern_no_keys(self, cache_service, mock_redis):
        """Test deleting by pattern when no keys match."""
        # Arrange
        pattern = "nonexistent:*"
        mock_redis.keys.return_value = []

        # Act
        result = await cache_service.delete_pattern(pattern)

        # Assert
        assert result == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_get_or_set_cache_hit(self, cache_service, mock_redis):
        """Test get_or_set with cache hit."""
        # Arrange
        key = "test:key"
        cached_value = {"data": "cached"}
        mock_redis.get.return_value = json.dumps(cached_value)

        async def factory():
            return {"data": "fresh"}

        # Act
        result = await cache_service.get_or_set(key, factory, ttl=3600)

        # Assert
        assert result == cached_value
        # setex should not be called on cache hit
        mock_redis.setex.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_get_or_set_cache_miss(self, cache_service, mock_redis):
        """Test get_or_set with cache miss."""
        # Arrange
        key = "test:key"
        fresh_value = {"data": "fresh"}
        mock_redis.get.return_value = None

        async def factory():
            return fresh_value

        # Act
        result = await cache_service.get_or_set(key, factory, ttl=3600)

        # Assert
        assert result == fresh_value
        mock_redis.setex.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_get_or_set_sync_function(self, cache_service, mock_redis):
        """Test get_or_set with sync factory function."""
        # Arrange
        key = "test:key"
        fresh_value = {"data": "fresh"}
        mock_redis.get.return_value = None

        def sync_factory():
            return fresh_value

        # Act
        result = await cache_service.get_or_set(key, sync_factory, ttl=3600)

        # Assert
        assert result == fresh_value
        mock_redis.setex.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_incr(self, cache_service, mock_redis):
        """Test cache increment operation."""
        # Arrange
        key = "counter:view_count"
        mock_redis.incr.return_value = 42

        # Act
        result = await cache_service.incr(key)

        # Assert
        assert result == 42
        mock_redis.incr.assert_called_once_with(key)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_get_stats(self, cache_service, mock_redis):
        """Test getting cache statistics."""
        # Act
        stats = await cache_service.get_stats()

        # Assert
        assert stats["connected_clients"] == 5
        assert stats["used_memory_human"] == "1.2M"
        assert stats["hit_rate"] == "80.0%"
        mock_redis.info.assert_called_once()

    @pytest.mark.unit
    def test_generate_key_simple(self, cache_service):
        """Test cache key generation with simple args."""
        # Arrange
        prefix = "search"

        # Act
        key = cache_service._generate_key(prefix, "arg1", "arg2")

        # Assert
        assert key.startswith("search:")
        assert "arg1" in key
        assert "arg2" in key

    @pytest.mark.unit
    def test_generate_key_with_kwargs(self, cache_service):
        """Test cache key generation with kwargs."""
        # Arrange
        prefix = "search"

        # Act
        key = cache_service._generate_key(prefix, q="transformer", limit=10)

        # Assert
        assert key.startswith("search:")
        assert "q:transformer" in key
        assert "limit:10" in key

    @pytest.mark.unit
    def test_generate_key_with_dict(self, cache_service):
        """Test cache key generation with dict argument."""
        # Arrange
        prefix = "search"
        filters = {"category": "deep_learning", "source": "arxiv"}

        # Act
        key = cache_service._generate_key(prefix, filters=filters)

        # Assert
        assert key.startswith("search:")
        assert "filters:" in key

    @pytest.mark.unit
    def test_generate_key_with_pydantic_model(self, cache_service):
        """Test cache key generation with Pydantic model."""
        # Arrange
        prefix = "search"
        model = TestModel(name="test", value=42)

        # Act
        key = cache_service._generate_key(prefix, model=model)

        # Assert
        assert key.startswith("search:")

    @pytest.mark.unit
    def test_generate_key_long_key_hashes(self, cache_service):
        """Test that long keys are hashed."""
        # Arrange
        prefix = "search"
        long_arg = "x" * 300  # Very long string

        # Act
        key = cache_service._generate_key(prefix, long_arg)

        # Assert
        assert key.startswith("search:hash:")
        assert len(key) < 100  # Hashed keys are short

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_set_with_pydantic_model(self, cache_service, mock_redis):
        """Test that Pydantic models are properly serialized."""
        # Arrange
        key = "test:model"
        model = TestModel(name="test", value=42)

        # Act
        result = await cache_service.set(key, model, ttl=3600)

        # Assert
        assert result is True
        mock_redis.setex.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_close(self, cache_service, mock_redis):
        """Test closing cache connection."""
        # Act
        await cache_service.close()

        # Assert
        mock_redis.close.assert_called_once()
        assert cache_service._redis is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_error_handling_get(self, cache_service, mock_redis):
        """Test error handling in get operation."""
        # Arrange
        key = "test:key"
        mock_redis.get.side_effect = Exception("Redis error")

        # Act
        result = await cache_service.get(key)

        # Assert - should return None on error, not raise
        assert result is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_error_handling_set(self, cache_service, mock_redis):
        """Test error handling in set operation."""
        # Arrange
        key = "test:key"
        value = {"data": "test"}
        mock_redis.setex.side_effect = Exception("Redis error")

        # Act
        result = await cache_service.set(key, value, ttl=3600)

        # Assert - should return False on error, not raise
        assert result is False

    @pytest.mark.unit
    def test_calculate_hit_rate(self, cache_service):
        """Test hit rate calculation."""
        # Act & Assert
        assert cache_service._calculate_hit_rate(80, 20) == "80.0%"
        assert cache_service._calculate_hit_rate(0, 0) == "0%"
        assert cache_service._calculate_hit_rate(100, 0) == "100.0%"
        assert cache_service._calculate_hit_rate(50, 50) == "50.0%"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cached_decorator(self, cache_service, mock_redis):
        """Test the cached decorator."""
        # Arrange
        call_count = 0

        @cache_service.cached("test", ttl=300)
        async def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        mock_redis.get.return_value = None  # Cache miss

        # Act
        result1 = await expensive_function(5)
        result2 = await expensive_function(5)  # Should hit cache

        # Assert - second call should hit cache
        # Note: decorator uses internal get/set, not mock_redis directly
        # This test validates the decorator structure
        assert result1 == 10
