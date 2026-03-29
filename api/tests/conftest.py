"""
Pytest configuration and fixtures for AI Frontiers API tests.
"""
import asyncio
import os
import json
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest


# Set test environment before importing app
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test_ai_frontiers"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_redis() -> AsyncMock:
    """Mock Redis client for unit tests."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.keys = AsyncMock(return_value=[])
    redis.exists = AsyncMock(return_value=0)
    return redis


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Mock database session for unit tests."""
    from sqlalchemy.ext.asyncio import AsyncSession
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.scalars = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def sample_content() -> dict:
    """Sample content data for testing."""
    return {
        "id": 1,
        "title": "Attention Is All You Need",
        "summary": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
        "original_url": "https://arxiv.org/abs/1706.03762",
        "source": "arxiv",
        "category": "deep_learning",
        "tags": ["transformer", "attention", "nlp"],
        "view_count": 1000,
        "like_count": 50,
        "published_at": "2023-01-15T10:00:00Z",
    }


@pytest.fixture
def sample_contents_list() -> list[dict]:
    """List of sample contents for testing."""
    return [
        {
            "id": 1,
            "title": "Attention Is All You Need",
            "summary": "The transformer architecture paper.",
            "original_url": "https://arxiv.org/abs/1706.03762",
            "source": "arxiv",
            "category": "deep_learning",
            "tags": ["transformer", "attention"],
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
def sample_search_result() -> dict:
    """Sample search result for testing."""
    return {
        "query": "transformer",
        "total": 2,
        "results": [
            {
                "id": 1,
                "title": "Attention Is All You Need",
                "score": 0.95,
            },
            {
                "id": 2,
                "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "score": 0.85,
            },
        ],
        "search_type": "hybrid",
    }


@pytest.fixture
def test_embedding() -> list[float]:
    """Sample embedding vector for testing (384 dimensions)."""
    # Simplified embedding for testing
    return [0.1] * 384


# Load fixtures from JSON files
@pytest.fixture
def fixture_contents() -> list[dict]:
    """Load sample contents from fixture file."""
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample_contents.json")
    if os.path.exists(fixture_path):
        with open(fixture_path, "r") as f:
            return json.load(f)
    return []
