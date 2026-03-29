"""
Integration tests for Contents API endpoints.
Tests parameter validation only - does not require database.
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


class TestContentsAPIValidation:
    """Test cases for Contents API parameter validation.
    These tests verify input validation without requiring database.
    """

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_contents_invalid_page_zero(self, client):
        """Test GET /api/v1/contents with page=0 (invalid, min is 1)."""
        response = await client.get("/api/v1/contents?page=0")
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_contents_invalid_page_negative(self, client):
        """Test GET /api/v1/contents with negative page."""
        response = await client.get("/api/v1/contents?page=-1")
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_contents_invalid_size_too_large(self, client):
        """Test GET /api/v1/contents with size > 100."""
        response = await client.get("/api/v1/contents?size=200")
        assert response.status_code == 422  # Validation error (max is 100)

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_contents_invalid_size_zero(self, client):
        """Test GET /api/v1/contents with size=0 (invalid, min is 1)."""
        response = await client.get("/api/v1/contents?size=0")
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_contents_invalid_size_negative(self, client):
        """Test GET /api/v1/contents with negative size."""
        response = await client.get("/api/v1/contents?size=-5")
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_popular_invalid_size_too_large(self, client):
        """Test GET /api/v1/contents/popular with size > 50."""
        response = await client.get("/api/v1/contents/popular?size=100")
        assert response.status_code == 422  # Validation error (max is 50)

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_popular_invalid_size_zero(self, client):
        """Test GET /api/v1/contents/popular with size=0."""
        response = await client.get("/api/v1/contents/popular?size=0")
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_popular_invalid_size_negative(self, client):
        """Test GET /api/v1/contents/popular with negative size."""
        response = await client.get("/api/v1/contents/popular?size=-1")
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_contents_endpoint_exists(self, client):
        """Test that the contents endpoint is registered by checking validation."""
        # Using non-integer page to trigger validation error
        response = await client.get("/api/v1/contents?page=abc")
        assert response.status_code == 422

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_popular_endpoint_exists(self, client):
        """Test that the popular endpoint is registered by checking validation."""
        # Using non-integer size to trigger validation error
        response = await client.get("/api/v1/contents/popular?size=abc")
        assert response.status_code == 422
