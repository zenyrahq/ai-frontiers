#!/usr/bin/env python3
"""
Create database tables directly with SQL
Bypass alembic migrations to avoid pgvector import issues in CI
"""
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import random
import asyncpg
from loguru import logger


from dotenv import load_dotenv

load_dotenv()

# Create test data inline (same as generate_test_data.py)
TEST_PAPERS = [
    {
        "title": "Attention Is All You Need",
        "summary": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.",
        "source": "arxiv",
        "category": "deep_learning",
        "tags": ["transformer", "attention", "nlp"],
        "views": 5000,
        "likes": 450,
    },
    {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers",
        "summary": "We introduce BERT, which stands for Bidirectional Encoder Representations from Transformers. BERT is designed to pre-train deep bidirectional representations from unlabeled text.",
        "source": "arxiv",
        "category": "natural_language",
        "tags": ["bert", "transformer", "pre-training"],
        "views": 4500,
        "likes": 420,
    },
    {
        "title": "GPT-4 Technical Report",
        "summary": "We report the development of GPT-4, a large-scale, multimodal model which can accept image and text inputs and produce text outputs. GPT-4 exhibits human-level performance on various benchmarks.",
        "source": "arxiv",
        "category": "generative_ai",
        "tags": ["gpt", "llm", "multimodal"],
        "views": 8000,
        "likes": 800,
    },
]


async def create_tables_and_seed_data():
    """Create tables directly and SQL and seed data"""
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        logger.error("DATABASE_URL not set")
        sys.exit(1)


    # Convert async URL to sync URL
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    # Connect to database
    conn = await asyncpg.connect(sync_url)

    try:
        # Create tables
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS contents (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                summary TEXT,
                content TEXT,
                original_url VARCHAR(1000) UNIQUE,
                source VARCHAR(100) NOT NULL,
                category VARCHAR(50),
                tags TEXT[],
                published_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                embedding TEXT,
                content_metadata JSONB,
                view_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                is_processed BOOLEAN DEFAULT false
            )
        """)

        logger.info("Created contents table")

        # Insert test data
        for i, paper in enumerate(TEST_PAPERS):
            days_ago = random.randint(1, 60)
            pub_date = datetime.now() - timedelta(days=days_ago)

            await conn.execute(
                """
                INSERT INTO contents (
                    title, summary, content, original_url, source, category, tags,
                    published_at, view_count, like_count, is_processed
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, true)
                """,
                paper["title"],
                paper["summary"],
                paper["summary"],
                f"https://arxiv.org/abs/2024.{10000 + i}",
                paper["source"],
                paper["category"],
                paper["tags"],
                pub_date,
                paper["views"] + random.randint(-100, 100),
                paper["likes"] + random.randint(-20, 20)
            )

        logger.info(f"Inserted: {paper['title']}")

        # Verify data
        count = await conn.fetchval("SELECT COUNT(*) FROM contents")
        logger.success(f"Database initialized with {count} records")

    finally:
        await conn.close()


async def main():
    logger.info("=" * 60)
    logger.info("Initializing database...")
    logger.info("=" * 60)

    await create_tables_and_seed_data()

    logger.info("=" * 60)
    logger.info("Database initialization complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
