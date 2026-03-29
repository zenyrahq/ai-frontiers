"""
Unit tests for SearchService.
Tests use mocking to isolate from database dependencies.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import asynccontextmanager
from datetime import datetime

from models.models import Content


def create_mock_content(data: dict) -> MagicMock:
    """Create a mock Content object from dict data."""
    content = MagicMock(spec=Content)
    content.id = data.get("id", 1)
    content.title = data.get("title", "Test Title")
    content.summary = data.get("summary", "Test summary")
    content.original_url = data.get("original_url", "https://example.com")
    content.source = data.get("source", "arxiv")
    content.category = data.get("category", "deep_learning")
    content.tags = data.get("tags", [])
    content.view_count = data.get("view_count", 0)
    content.like_count = data.get("like_count", 0)
    content.published_at = data.get("published_at", datetime.now())
    content.embedding = data.get("embedding", [0.1] * 384)
    content.is_processed = data.get("is_processed", True)
    return content


class TestSearchService:
    """Test cases for SearchService."""

    @pytest.fixture
    def mock_session(self):
        """Create mock async session."""
        session = AsyncMock()
        session.execute = AsyncMock()
        session.scalar = AsyncMock()
        session.scalars = AsyncMock()
        return session

    @pytest.fixture
    def sample_content_data(self) -> list[dict]:
        """Sample content data for testing."""
        return [
            {
                "id": 1,
                "title": "Attention Is All You Need",
                "summary": "The transformer architecture paper.",
                "original_url": "https://arxiv.org/abs/1706.03762",
                "source": "arxiv",
                "category": "deep_learning",
                "tags": ["transformer", "attention", "nlp"],
                "view_count": 1000,
                "like_count": 50,
            },
            {
                "id": 2,
                "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "summary": "A new language representation model.",
                "original_url": "https://arxiv.org/abs/1810.04805",
                "source": "arxiv",
                "category": "natural_language",
                "tags": ["bert", "transformer", "pretraining"],
                "view_count": 800,
                "like_count": 40,
            },
            {
                "id": 3,
                "title": "GPT-4 Technical Report",
                "summary": "A large-scale multimodal model.",
                "original_url": "https://arxiv.org/abs/2303.08774",
                "source": "arxiv",
                "category": "large_language_models",
                "tags": ["gpt", "llm", "multimodal"],
                "view_count": 2000,
                "like_count": 100,
            },
        ]

    @pytest.fixture
    def test_embedding(self) -> list[float]:
        """Sample embedding vector for testing (384 dimensions)."""
        return [0.1] * 384

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_vector_search_success(self, mock_session, sample_content_data, test_embedding):
        """Test vector search returns similar contents."""
        # Arrange
        mock_contents = [create_mock_content(d) for d in sample_content_data]
        mock_result = MagicMock()
        mock_result.all.return_value = [(mock_contents[0], 0.95), (mock_contents[1], 0.85)]
        mock_session.execute.return_value = mock_result

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act
            results = await service.vector_search(test_embedding, limit=5)

        # Assert
        assert len(results) == 2
        assert results[0][1] == 0.95  # similarity score

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_vector_search_no_results(self, mock_session, test_embedding):
        """Test vector search with no results."""
        # Arrange
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute.return_value = mock_result

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act
            results = await service.vector_search(test_embedding, limit=5)

        # Assert
        assert results == []

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_vector_search_with_filters(self, mock_session, sample_content_data, test_embedding):
        """Test vector search with category filter."""
        # Arrange
        filtered_data = [d for d in sample_content_data if d["category"] == "deep_learning"]
        mock_contents = [create_mock_content(d) for d in filtered_data]
        mock_result = MagicMock()
        mock_result.all.return_value = [(mock_contents[0], 0.92)]
        mock_session.execute.return_value = mock_result

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act
            results = await service.vector_search(
                test_embedding,
                limit=5,
                filters={"category": "deep_learning"}
            )

        # Assert
        assert len(results) == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_fulltext_search_success(self, mock_session, sample_content_data):
        """Test full-text search with keywords."""
        # Arrange
        # Create mock row objects that can be accessed like named tuples
        mock_row = MagicMock()
        mock_row.id = 1
        mock_row.title = sample_content_data[0]["title"]
        mock_row.summary = sample_content_data[0]["summary"]
        mock_row.original_url = sample_content_data[0]["original_url"]
        mock_row.source = sample_content_data[0]["source"]
        mock_row.category = sample_content_data[0]["category"]
        mock_row.tags = sample_content_data[0]["tags"]
        mock_row.published_at = datetime.now()
        mock_row.view_count = sample_content_data[0]["view_count"]
        mock_row.like_count = sample_content_data[0]["like_count"]
        mock_row.rank = 0.85

        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act
            results = await service.fulltext_search("transformer", limit=10)

        # Assert
        assert len(results) == 1
        assert results[0][1] == 0.85  # rank score

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_fulltext_search_empty_query(self, mock_session):
        """Test full-text search with empty query returns empty."""
        # Arrange
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute.return_value = mock_result

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act
            results = await service.fulltext_search("", limit=10)

        # Assert - empty query should still work, just return no results
        assert results == []

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_hybrid_search_combines_results(self, mock_session, sample_content_data, test_embedding):
        """Test hybrid search combines vector and full-text results."""
        # Arrange - mock vector search
        mock_content1 = create_mock_content(sample_content_data[0])
        mock_content2 = create_mock_content(sample_content_data[1])

        # First call for vector search
        vector_result = MagicMock()
        vector_result.all.return_value = [(mock_content1, 0.9)]

        # Second call for fulltext search
        mock_row = MagicMock()
        mock_row.id = 2
        mock_row.title = sample_content_data[1]["title"]
        mock_row.summary = sample_content_data[1]["summary"]
        mock_row.original_url = sample_content_data[1]["original_url"]
        mock_row.source = sample_content_data[1]["source"]
        mock_row.category = sample_content_data[1]["category"]
        mock_row.tags = sample_content_data[1]["tags"]
        mock_row.published_at = datetime.now()
        mock_row.view_count = sample_content_data[1]["view_count"]
        mock_row.like_count = sample_content_data[1]["like_count"]
        mock_row.rank = 0.8

        fulltext_result = MagicMock()
        fulltext_result.all.return_value = [mock_row]

        mock_session.execute.side_effect = [vector_result, fulltext_result]

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act - hybrid_search requires both query and query_embedding
            results = await service.hybrid_search(
                query="transformer",
                query_embedding=test_embedding,
                limit=10,
                vector_weight=0.6
            )

        # Assert
        assert len(results) >= 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_by_category(self, mock_session, sample_content_data):
        """Test search filtered by category."""
        # Arrange
        filtered_data = [d for d in sample_content_data if d["category"] == "deep_learning"]
        mock_contents = [create_mock_content(d) for d in filtered_data]

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_contents

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act
            results = await service.search_by_category("deep_learning", limit=10)

        # Assert
        assert len(results) == 1
        assert results[0].category == "deep_learning"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_by_tags_any(self, mock_session, sample_content_data):
        """Test search by tags with any match (overlap)."""
        # Arrange - return first two items (both have 'transformer')
        mock_contents = [create_mock_content(d) for d in sample_content_data[:2]]

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_contents

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act
            results = await service.search_by_tags(
                ["transformer", "attention"],
                match_all=False,
                limit=10
            )

        # Assert
        assert len(results) >= 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_by_tags_all(self, mock_session, sample_content_data):
        """Test search by tags requiring all tags (contains)."""
        # Arrange - only first item has both 'transformer' and 'nlp'
        mock_contents = [create_mock_content(sample_content_data[0])]

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_contents

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act
            results = await service.search_by_tags(
                ["transformer", "nlp"],
                match_all=True,
                limit=10
            )

        # Assert
        assert len(results) == 1
        assert "transformer" in results[0].tags
        assert "nlp" in results[0].tags

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_popular_contents(self, mock_session, sample_content_data):
        """Test getting popular contents sorted by view count."""
        # Arrange - sort by view_count descending
        sorted_data = sorted(sample_content_data, key=lambda x: x["view_count"], reverse=True)
        mock_contents = [create_mock_content(d) for d in sorted_data]

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_contents

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act
            results = await service.get_popular_contents(days=7, limit=10)

        # Assert - should be sorted by popularity (view_count + like_count * 2)
        assert len(results) == 3
        # GPT-4 has highest combined score (2000 + 100*2 = 2200)
        assert results[0].title == "GPT-4 Technical Report"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_related_contents(self, mock_session, sample_content_data, test_embedding):
        """Test getting related contents for a specific content."""
        # Arrange
        source_content = create_mock_content(sample_content_data[0])
        source_content.embedding = test_embedding

        related_content = create_mock_content(sample_content_data[1])

        # First call gets source content
        mock_scalar_result = MagicMock()
        mock_scalar_result.scalar_one_or_none.return_value = source_content

        # Second call (vector_search) returns related
        mock_vector_result = MagicMock()
        mock_vector_result.all.return_value = [(source_content, 0.95), (related_content, 0.85)]

        mock_session.execute.side_effect = [mock_scalar_result, mock_vector_result]

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act
            results = await service.get_related_contents(content_id=1, limit=5)

        # Assert
        assert len(results) == 2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_related_contents_not_found(self, mock_session):
        """Test getting related contents when source not found."""
        # Arrange
        mock_scalar_result = MagicMock()
        mock_scalar_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_scalar_result

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act
            results = await service.get_related_contents(content_id=999, limit=5)

        # Assert
        assert results == []

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_search_suggestions(self, mock_session):
        """Test getting search suggestions based on partial query."""
        # Arrange
        mock_result = MagicMock()
        mock_result.all.return_value = [
            ("Attention Is All You Need",),
            ("BERT: Pre-training of Deep Bidirectional Transformers",),
        ]
        mock_session.execute.return_value = mock_result

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act
            suggestions = await service.get_search_suggestions("trans", limit=5)

        # Assert
        assert len(suggestions) == 2
        assert "Attention" in suggestions[0]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_search_suggestions_no_results(self, mock_session):
        """Test search suggestions with no matches."""
        # Arrange
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute.return_value = mock_result

        @asynccontextmanager
        async def mock_session_local():
            yield mock_session

        with patch("services.search_service.AsyncSessionLocal", mock_session_local):
            from services.search_service import SearchService
            service = SearchService()

            # Act
            suggestions = await service.get_search_suggestions("zzzzzzz", limit=5)

        # Assert
        assert suggestions == []
