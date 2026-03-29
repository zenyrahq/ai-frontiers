"""
Integration tests for Contents API endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock
import json


@pytest.fixture
async def client():
    """Create async test client."""
    from main import app
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


class TestContentsAPI:
    """Test cases for Contents API endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_contents_default(self, client, sample_contents_list):
        """Test GET /api/v1/contents with default parameters."""
        # Arrange
        with patch("routes.contents.get_contents_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_contents.return_value = {
                "items": sample_contents_list,
                "total": len(sample_contents_list),
                "page": 1,
                "size": 20,
                "pages": 1
            }
            mock_service.return_value = mock_instance

            # Act
            response = await client.get("/api/v1/contents")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total" in data

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_contents_pagination(self, client, sample_contents_list):
        """Test GET /api/v1/contents with pagination."""
        # Arrange
        with patch("routes.contents.get_contents_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_contents.return_value = {
                "items": sample_contents_list[:2],
                "total": len(sample_contents_list),
                "page": 1,
                "size": 2,
                "pages": 3
            }
            mock_service.return_value = mock_instance

            # Act
            response = await client.get("/api/v1/contents?page=1&size=2")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["page"] == 1
            assert data["size"] == 2

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_contents_filter_by_category(self, client, sample_contents_list):
        """Test GET /api/v1/contents filtered by category."""
        # Arrange
        category = "deep_learning"
        filtered = [c for c in sample_contents_list if c["category"] == category]

        with patch("routes.contents.get_contents_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_contents.return_value = {
                "items": filtered,
                "total": len(filtered),
                "page": 1,
                "size": 20,
                "pages": 1
            }
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/contents?category={category}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            for item in data["items"]:
                assert item["category"] == category

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_contents_filter_by_source(self, client, sample_contents_list):
        """Test GET /api/v1/contents filtered by source."""
        # Arrange
        source = "arxiv"
        filtered = [c for c in sample_contents_list if c["source"] == source]

        with patch("routes.contents.get_contents_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_contents.return_value = {
                "items": filtered,
                "total": len(filtered),
                "page": 1,
                "size": 20,
                "pages": 1
            }
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/contents?source={source}")

            # Assert
            assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_content_by_id_exists(self, client, sample_content):
        """Test GET /api/v1/contents/{id} when content exists."""
        # Arrange
        content_id = 1
        with patch("routes.contents.get_contents_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_content_by_id.return_value = sample_content
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/contents/{content_id}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == content_id

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_content_by_id_not_found(self, client):
        """Test GET /api/v1/contents/{id} when content not found."""
        # Arrange
        content_id = 99999
        with patch("routes.contents.get_contents_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_content_by_id.return_value = None
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/contents/{content_id}")

            # Assert
            assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_popular_contents(self, client, sample_contents_list):
        """Test GET /api/v1/contents/popular endpoint."""
        # Arrange
        sorted_contents = sorted(
            sample_contents_list,
            key=lambda x: x["view_count"],
            reverse=True
        )
        with patch("routes.contents.get_contents_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_popular_contents.return_value = sorted_contents
            mock_service.return_value = mock_instance

            # Act
            response = await client.get("/api/v1/contents/popular")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data) > 0

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_related_contents(self, client, sample_contents_list):
        """Test GET /api/v1/contents/{id}/related endpoint."""
        # Arrange
        content_id = 1
        related = sample_contents_list[1:3]
        with patch("routes.contents.get_contents_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_related_contents.return_value = related
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/contents/{content_id}/related")

            # Assert
            assert response.status_code == 200
            data = response.json()
            # Should not include the source content
            assert all(item["id"] != content_id for item in data)

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_increment_view_count(self, client, sample_content):
        """Test that viewing content increments view count."""
        # Arrange
        content_id = 1
        with patch("routes.contents.get_contents_service") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.increment_view_count.return_value = True
            mock_instance.get_content_by_id.return_value = {
                **sample_content,
                "view_count": sample_content["view_count"] + 1
            }
            mock_service.return_value = mock_instance

            # Act
            response = await client.get(f"/api/v1/contents/{content_id}")

            # Assert
            assert response.status_code == 200
