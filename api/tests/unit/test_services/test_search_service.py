"""
Unit tests for SearchService.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np


class TestSearchService:
    """Test cases for SearchService."""

    @pytest.fixture
    def search_service(self, mock_db_session, mock_redis):
        """Create SearchService instance with mocked dependencies."""
        with patch("services.search_service.get_db", return_value=mock_db_session):
            with patch("services.search_service.get_redis", return_value=mock_redis):
                from services.search_service import SearchService
                yield SearchService()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_vector_search_success(self, search_service, mock_db_session, sample_contents_list):
        """Test vector search returns similar contents."""
        # Arrange
        query_embedding = [0.1] * 384
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_contents_list
        mock_db_session.execute.return_value = mock_result

        # Act
        results = await search_service.vector_search(query_embedding, limit=5)

        # Assert
        assert results is not None
        assert len(results) == len(sample_contents_list)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_vector_search_no_results(self, search_service, mock_db_session):
        """Test vector search with no results."""
        # Arrange
        query_embedding = [0.1] * 384
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        # Act
        results = await search_service.vector_search(query_embedding, limit=5)

        # Assert
        assert results == []

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_fulltext_search(self, search_service, mock_db_session, sample_contents_list):
        """Test full-text search with keywords."""
        # Arrange
        query = "transformer"
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_contents_list[:2]
        mock_db_session.execute.return_value = mock_result

        # Act
        results = await search_service.fulltext_search(query, limit=10)

        # Assert
        assert len(results) == 2
        mock_db_session.execute.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_hybrid_search_weights(self, search_service, mock_db_session, sample_contents_list):
        """Test hybrid search applies correct weights."""
        # Arrange
        query = "attention"
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_contents_list
        mock_db_session.execute.return_value = mock_result

        # Act
        results = await search_service.hybrid_search(
            query=query,
            vector_weight=0.6,
            fulltext_weight=0.4,
            limit=10
        )

        # Assert
        assert results is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_by_category(self, search_service, mock_db_session, sample_contents_list):
        """Test search filtered by category."""
        # Arrange
        category = "deep_learning"
        filtered = [c for c in sample_contents_list if c["category"] == category]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = filtered
        mock_db_session.execute.return_value = mock_result

        # Act
        results = await search_service.search_by_category(category, limit=10)

        # Assert
        for item in results:
            assert item["category"] == category

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_by_tags_any(self, search_service, mock_db_session, sample_contents_list):
        """Test search by tags with any match."""
        # Arrange
        tags = ["transformer", "attention"]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_contents_list[:2]
        mock_db_session.execute.return_value = mock_result

        # Act
        results = await search_service.search_by_tags(tags, match_all=False, limit=10)

        # Assert
        assert len(results) >= 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_by_tags_all(self, search_service, mock_db_session, sample_contents_list):
        """Test search by tags requiring all tags."""
        # Arrange
        tags = ["transformer", "nlp"]
        mock_result = MagicMock()
        # Only first item has both tags
        mock_result.scalars.return_value.all.return_value = [sample_contents_list[0]]
        mock_db_session.execute.return_value = mock_result

        # Act
        results = await search_service.search_by_tags(tags, match_all=True, limit=10)

        # Assert
        for item in results:
            item_tags = set(item["tags"])
            assert all(t in item_tags for t in tags)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_popular_contents(self, search_service, mock_db_session, sample_contents_list):
        """Test getting popular contents sorted by view count."""
        # Arrange
        sorted_contents = sorted(sample_contents_list, key=lambda x: x["view_count"], reverse=True)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sorted_contents
        mock_db_session.execute.return_value = mock_result

        # Act
        results = await search_service.get_popular_contents(days=7, limit=10)

        # Assert
        assert results[0]["view_count"] >= results[-1]["view_count"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_related_contents(self, search_service, mock_db_session, sample_contents_list):
        """Test getting related contents for a specific content."""
        # Arrange
        content_id = 1
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_contents_list[1:3]
        mock_db_session.execute.return_value = mock_result

        # Act
        results = await search_service.get_related_contents(content_id, limit=5)

        # Assert
        assert len(results) == 2
        # Should not include the source content
        assert all(r["id"] != content_id for r in results)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_search_suggestions(self, search_service, mock_db_session, sample_contents_list):
        """Test getting search suggestions based on partial query."""
        # Arrange
        partial_query = "trans"
        expected_titles = ["Attention Is All You Need", "BERT: Pre-training of Deep Bidirectional Transformers"]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            MagicMock(title=title) for title in expected_titles
        ]
        mock_db_session.execute.return_value = mock_result

        # Act
        suggestions = await search_service.get_search_suggestions(partial_query, limit=5)

        # Assert
        assert len(suggestions) <= 5
        assert all(len(s) >= 3 for s in suggestions)
