"""
Configuration module
Load settings from environment variables
"""
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings

    Automatically loaded from environment variables
    """

    # Application basic settings
    APP_NAME: str = "AI Frontiers API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4

    # Database settings
    DATABASE_URL: str = "postgresql://aifrontiers:password@localhost:5432/aifrontiers"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""

    # Elasticsearch settings
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX_PREFIX: str = "aifrontiers"

    # AI API settings
    ANTHROPIC_API_KEY: str = "sk-ant-test-placeholder"
    OPENAI_API_KEY: str = "sk-test-placeholder"
    TRANSLATION_SERVICE: str = "claude"

    # Security settings
    SECRET_KEY: str = "ai-frontiers-dev-secret-key-2024-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Crawler settings
    CRAWLER_INTERVAL_MINUTES: int = 15
    CRAWLER_MAX_RETRIES: int = 3
    CRAWLER_TIMEOUT: int = 30

    # Recommendation system settings
    RECOMMENDATION_CACHE_TTL: int = 900
    RECOMMENDATION_TOP_K: int = 20

    # Monitoring settings
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

    class Config:
        # Find .env file in project root (parent of api directory)
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env file


# Global settings instance
settings = Settings()
