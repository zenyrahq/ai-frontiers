"""
Database Service for Crawler
Handles storing and managing crawled content in database
"""
import sys
import os
from pathlib import Path

# Add api directory to path for imports
api_path = Path(__file__).parent.parent.parent / "api"
sys.path.insert(0, str(api_path))

from typing import List, Optional
from datetime import datetime
from loguru import logger
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from models.models import Content
from services.arxiv_service import ArxivPaper


class DatabaseService:
    """
    Database service for managing content storage
    """

    async def store_paper(self, paper: ArxivPaper) -> Optional[Content]:
        """
        Store a single paper in the database

        Args:
            paper: ArxivPaper object to store

        Returns:
            Created Content object or None if duplicate
        """
        async with AsyncSessionLocal() as session:
            try:
                # Check for duplicates
                existing = await self._check_duplicate(session, paper.id)
                if existing:
                    logger.debug(f"Paper {paper.id} already exists, skipping")
                    return None

                # Create new content record
                content = Content(
                    title=paper.title,
                    summary=paper.abstract,
                    content=paper.abstract,  # Use abstract as content for now
                    original_url=paper.arxiv_url,
                    source="arxiv",
                    category=self._map_category(paper.primary_category),
                    tags=paper.categories,
                    published_at=paper.published_at,
                    is_processed=False,
                    view_count=0,
                    like_count=0
                )

                session.add(content)
                await session.commit()
                await session.refresh(content)

                logger.info(f"✅ Stored paper: {paper.id} - {paper.title[:50]}...")
                return content

            except Exception as e:
                logger.error(f"Error storing paper {paper.id}: {e}")
                await session.rollback()
                return None

    async def store_papers_batch(
        self,
        papers: List[ArxivPaper],
        batch_size: int = 50
    ) -> int:
        """
        Store multiple papers in batches

        Args:
            papers: List of ArxivPaper objects
            batch_size: Number of papers to process in each batch

        Returns:
            Number of successfully stored papers
        """
        stored_count = 0

        for i in range(0, len(papers), batch_size):
            batch = papers[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} papers)")

            for paper in batch:
                result = await self.store_paper(paper)
                if result:
                    stored_count += 1

            # Small delay between batches
            import asyncio
            await asyncio.sleep(0.5)

        logger.info(f"✅ Stored {stored_count}/{len(papers)} papers")
        return stored_count

    async def _check_duplicate(
        self,
        session: AsyncSession,
        paper_id: str
    ) -> bool:
        """
        Check if paper already exists in database

        Args:
            session: Database session
            paper_id: arXiv paper ID

        Returns:
            True if duplicate exists
        """
        # Check by URL which contains the paper ID
        url = f"http://arxiv.org/abs/{paper_id}"
        query = select(Content).where(Content.original_url == url)
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None

    def _map_category(self, arxiv_category: Optional[str]) -> str:
        """
        Map arXiv category to our category system

        Args:
            arxiv_category: arXiv category (e.g., "cs.AI")

        Returns:
            Our category name
        """
        if not arxiv_category:
            return "general"

        category_mapping = {
            "cs.AI": "artificial_intelligence",
            "cs.LG": "machine_learning",
            "cs.CL": "natural_language_processing",
            "cs.CV": "computer_vision",
            "cs.NE": "neural_computing",
            "cs.RO": "robotics",
            "stat.ML": "machine_learning",
        }

        return category_mapping.get(arxiv_category, "general")

    async def get_unprocessed_contents(
        self,
        limit: int = 100
    ) -> List[Content]:
        """
        Get unprocessed contents for NLP processing

        Args:
            limit: Maximum number of contents to retrieve

        Returns:
            List of unprocessed Content objects
        """
        async with AsyncSessionLocal() as session:
            query = (
                select(Content)
                .where(Content.is_processed == False)
                .order_by(Content.created_at.desc())
                .limit(limit)
            )

            result = await session.execute(query)
            return result.scalars().all()

    async def mark_as_processed(self, content_id: int) -> bool:
        """
        Mark content as processed

        Args:
            content_id: Content ID

        Returns:
            Success status
        """
        async with AsyncSessionLocal() as session:
            try:
                query = select(Content).where(Content.id == content_id)
                result = await session.execute(query)
                content = result.scalar_one_or_none()

                if content:
                    content.is_processed = True
                    await session.commit()
                    return True

                return False

            except Exception as e:
                logger.error(f"Error marking content {content_id} as processed: {e}")
                await session.rollback()
                return False

    async def get_stats(self) -> dict:
        """
        Get crawler statistics

        Returns:
            Statistics dictionary
        """
        async with AsyncSessionLocal() as session:
            from sqlalchemy import func

            # Total count
            total_query = select(func.count(Content.id))
            total = await session.scalar(total_query)

            # Unprocessed count
            unprocessed_query = select(func.count(Content.id)).where(
                Content.is_processed == False
            )
            unprocessed = await session.scalar(unprocessed_query)

            # Count by source
            source_query = (
                select(Content.source, func.count(Content.id))
                .group_by(Content.source)
            )
            source_result = await session.execute(source_query)
            by_source = dict(source_result.all())

            return {
                "total": total,
                "unprocessed": unprocessed,
                "processed": total - unprocessed,
                "by_source": by_source,
            }
