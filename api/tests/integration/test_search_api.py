"""
Integration tests for Search API endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.fixture
async def client():
    """Create async test client."""
    from main import app
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


class TestSearchAPI:
    """Test cases for Search API endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_hybrid_search_success(self, client, sample_search_result, sample_contents_list):
        """Test GET /api/v1/search with valid query."""
        # Arrange
        query = "transformer"
        with patch("routes.search.get_search_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.hybrid_search.return_value = {
                "query": query,
                "total": len(sample_contents_list),
                "results": sample_contents_list,
                "search_type": "hybrid"
            }
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/search?q={query}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["query"] == query
            assert "results" in data
            assert data["search_type"] == "hybrid"

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_hybrid_search_empty_query(self, client):
        """Test GET /api/v1/search with empty query returns error."""
        # Act
        response = await client.get("/api/v1/search?q=")

        # Assert
        assert response.status_code == 422

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_hybrid_search_with_filters(self, client, sample_contents_list):
        """Test hybrid search with category filter."""
        # Arrange
        query = "neural network"
        category = "deep_learning"
        with patch("routes.search.get_search_service") as mock_service:
            mock_instance = AsyncMock()
            filtered = [c for c in sample_contents_list if c["category"] == category]
            mock_instance.hybrid_search.return_value = {
                "query": query,
                "total": len(filtered),
                "results": filtered,
                "search_type": "hybrid",
                "filters": {"category": category}
            }
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/search?q={query}&category={category}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["filters"]["category"] == category

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_vector_search_endpoint(self, client, sample_contents_list):
        """Test GET /api/v1/search/vector endpoint."""
        # Arrange
        query = "attention mechanism"
        with patch("routes.search.get_search_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.vector_search.return_value = sample_contents_list[:2]
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/search/vector?q={query}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "results" in data

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_fulltext_search_endpoint(self, client, sample_contents_list):
        """Test GET /api/v1/search/fulltext endpoint."""
        # Arrange
        query = "deep learning"
        with patch("routes.search.get_search_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.fulltext_search.return_value = sample_contents_list
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/search/fulltext?q={query}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "results" in data

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_search_suggestions_endpoint(self, client):
        """Test GET /api/v1/search/suggestions endpoint."""
        # Arrange
        partial_query = "trans"
        expected_suggestions = [
            "transformer",
            "transformer architecture",
            "attention transformer"
        ]
        with patch("routes.search.get_search_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_search_suggestions.return_value = expected_suggestions
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/search/suggestions?q={partial_query}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "suggestions" in data
            assert len(data["suggestions"]) <= 10

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_search_by_category_endpoint(self, client, sample_contents_list):
        """Test GET /api/v1/search/category/{category} endpoint."""
        # Arrange
        category = "deep_learning"
        with patch("routes.search.get_search_service") as mock_service:
            mock_instance = AsyncMock()
            filtered = [c for c in sample_contents_list if c["category"] == category]
            mock_instance.search_by_category.return_value = {
                "category": category,
                "total": len(filtered),
                "results": filtered
            }
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/search/category/{category}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["category"] == category

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_search_by_tags_endpoint(self, client, sample_contents_list):
        """Test GET /api/v1/search/tags endpoint."""
        # Arrange
        tags = "transformer,attention"
        with patch("routes.search.get_search_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.search_by_tags.return_value = {
                "tags": tags.split(","),
                "total": 2,
                "results": sample_contents_list[:2]
            }
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/search/tags?tags={tags}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "tags" in data
            assert "results" in data

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_search_popular_endpoint(self, client, sample_contents_list):
        """Test GET /api/v1/search/popular endpoint."""
        # Arrange
        with patch("routes.search.get_search_service") as mock_service:
            mock_instance = AsyncMock()
            sorted_contents = sorted(
                sample_contents_list,
                key=lambda x: x.get("view_count", 0),
                reverse=True
            )
            mock_instance.get_popular_contents.return_value = {
                "query": "popular:7days",
                "total": len(sorted_contents),
                "results": sorted_contents,
                "search_type": "popular"
            }
            mock_service.return_value = mock_instance

            # Act
            response = await client.get("/api/v1/search/popular")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["search_type"] == "popular"

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_search_related_endpoint(self, client, sample_contents_list):
        """Test GET /api/v1/search/related/{id} endpoint."""
        # Arrange
        content_id = 1
        with patch("routes.search.get_search_service") as mock_service:
            mock_instance = AsyncMock()
            related = [c for c in sample_contents_list if c["id"] != content_id]
            mock_instance.get_related_contents.return_value = {
                "content_id": content_id,
                "total": len(related),
                "results": related
            }
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/search/related/{content_id}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["content_id"] == content_id

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_search_pagination(self, client, sample_contents_list):
        """Test search results pagination."""
        # Arrange
        query = "AI"
        with patch("routes.search.get_search_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.hybrid_search.return_value = {
                "query": query,
                "total": len(sample_contents_list),
                "results": sample_contents_list[:2],
                "page": 1,
                "size": 2,
                "pages": 3,
                "search_type": "hybrid"
            }
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/search?q={query}&page=1&size=2")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "page" in data
            assert "size" in data
            assert "pages" in data
