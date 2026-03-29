"""
Unit tests for CacheService.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import asyncio


class TestCacheService:
    """Test cases for CacheService."""

    @pytest.fixture
    def cache_service(self, mock_redis):
        """Create CacheService instance with mocked Redis."""
        with patch("services.cache_service.get_redis", return_value=mock_redis):
            from services.cache_service import CacheService
            yield CacheService()

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
        mock_redis.set.assert_called_once()

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
        assert result == 1
        mock_redis.delete.assert_called_once_with(key)

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

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_exists_true(self, cache_service, mock_redis):
        """Test cache exists returns True."""
        # Arrange
        key = "test:key"
        mock_redis.exists.return_value = 1

        # Act
        result = await cache_service.exists(key)

        # Assert
        assert result is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_exists_false(self, cache_service, mock_redis):
        """Test cache exists returns False."""
        # Arrange
        key = "test:nonexistent"
        mock_redis.exists.return_value = 0

        # Act
        result = await cache_service.exists(key)

        # Assert
        assert result is False

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
        # Factory should not be called on cache hit
        mock_redis.set.assert_not_called()

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
        mock_redis.set.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_increment(self, cache_service, mock_redis):
        """Test cache increment operation."""
        # Arrange
        key = "counter:view_count"
        mock_redis.incr.return_value = 42

        # Act
        result = await cache_service.increment(key)

        # Assert
        assert result == 42
        mock_redis.incr.assert_called_once_with(key)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_expire(self, cache_service, mock_redis):
        """Test setting TTL on existing key."""
        # Arrange
        key = "test:key"
        ttl = 1800
        mock_redis.expire.return_value = True

        # Act
        result = await cache_service.expire(key, ttl)

        # Assert
        assert result is True
        mock_redis.expire.assert_called_once_with(key, ttl)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_cache_key(self, cache_service):
        """Test cache key generation."""
        # Arrange
        prefix = "search"
        params = {"q": "transformer", "limit": 10}

        # Act
        key = cache_service.generate_key(prefix, **params)

        # Assert
        assert key.startswith("search:")
        assert len(key) > len("search:")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_set_with_json_serialization(self, cache_service, mock_redis):
        """Test that complex objects are properly serialized."""
        # Arrange
        key = "test:complex"
        value = {
            "items": [1, 2, 3],
            "nested": {"a": "b"},
            "number": 42
        }

        # Act
        result = await cache_service.set(key, value, ttl=3600)

        # Assert
        assert result is True
        call_args = mock_redis.set.call_args
        serialized = call_args[0][1]
        assert json.loads(serialized) == value
