"""
Integration tests for Health API endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.fixture
async def client():
    """Create async test client."""
    from main import app
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


class TestHealthAPI:
    """Test cases for Health API endpoints."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test health check endpoint returns 200."""
        # Act
        response = await client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_health_check_response_format(self, client):
        """Test health check response has correct format."""
        # Act
        response = await client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        # Act
        response = await client.get("/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "status" in data
