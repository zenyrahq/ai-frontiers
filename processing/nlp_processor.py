"""
NLP Processor
Main processing service that coordinates all NLP operations
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

# Add api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from core.config import settings
from models.models import Content
from core.database import AsyncSessionLocal
from sqlalchemy import select, update

from services.claude_service import ClaudeService, ProcessedContent
from services.embedding_service import get_embedding_service


class NLPProcessor:
    """
    NLP Processing service

    Orchestrates:
    1. Content summarization (Claude API)
    2. Keyword extraction (Claude API)
    3. Entity recognition (Claude API)
    4. Vector embedding generation (Sentence Transformers)
    5. Database updates
    """

    def __init__(self):
        """Initialize NLP processor"""
        self.claude_service = ClaudeService(
            api_key=settings.ANTHROPIC_API_KEY
        )
        self.embedding_service = get_embedding_service(
            model_name="all-MiniLM-L6-v2",
            device="cpu"
        )

        logger.info("NLP Processor initialized")

    async def process_content(self, content: Content) -> bool:
        """
        Process a single content item

        Args:
            content: Content object to process

        Returns:
            Success status
        """
        try:
            logger.info(f"Processing content {content.id}: {content.title[:50]}...")

            # Step 1: Generate summary, keywords, entities using Claude
            processed = await self.claude_service.process_content(
                title=content.title,
                abstract=content.summary or "",
                categories=content.tags if content.tags else None
            )

            # Step 2: Generate vector embedding
            # Combine title + summary for better semantic representation
            text_for_embedding = f"{content.title}\n\n{processed.summary}"
            embedding = await self.embedding_service.generate_embedding_async(
                text_for_embedding
            )

            # Step 3: Update database
            async with AsyncSessionLocal() as session:
                # Fetch fresh content
                query = select(Content).where(Content.id == content.id)
                result = await session.execute(query)
                db_content = result.scalar_one_or_none()

                if db_content:
                    # Update fields
                    if processed.summary:
                        db_content.summary = processed.summary

                    if processed.keywords:
                        if db_content.tags:
                            # Merge with existing tags
                            existing_tags = set(db_content.tags)
                            new_tags = set(processed.keywords)
                            db_content.tags = list(existing_tags | new_tags)
                        else:
                            db_content.tags = processed.keywords

                    if processed.category:
                        db_content.category = processed.category

                    if embedding:
                        db_content.embedding = embedding

                    # Update metadata
                    if not db_content.content_metadata:
                        db_content.content_metadata = {}

                    db_content.content_metadata.update({
                        "keywords": processed.keywords,
                        "entities": processed.entities,
                        "importance_score": processed.importance_score,
                        "sentiment": processed.sentiment,
                        "processed_at": datetime.utcnow().isoformat()
                    })

                    # Mark as processed
                    db_content.is_processed = True

                    await session.commit()
                    logger.success(f"✅ Processed content {content.id}")
                    return True

        except Exception as e:
            logger.error(f"Error processing content {content.id}: {e}")
            return False

        return False

    async def process_batch(
        self,
        limit: int = 100,
        batch_size: int = 10
    ) -> Dict[str, int]:
        """
        Process multiple unprocessed contents

        Args:
            limit: Maximum number of contents to process
            batch_size: Batch size for parallel processing

        Returns:
            Statistics dictionary
        """
        logger.info(f"Starting batch processing (limit: {limit})")

        stats = {
            "total": 0,
            "success": 0,
            "failed": 0
        }

        try:
            # Fetch unprocessed contents
            async with AsyncSessionLocal() as session:
                query = (
                    select(Content)
                    .where(Content.is_processed == False)
                    .order_by(Content.created_at.desc())
                    .limit(limit)
                )

                result = await session.execute(query)
                contents = result.scalars().all()

                stats["total"] = len(contents)
                logger.info(f"Found {stats['total']} unprocessed contents")

            # Process in batches
            for i in range(0, len(contents), batch_size):
                batch = contents[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} items)")

                # Process concurrently
                tasks = [self.process_content(content) for content in batch]
                results = await asyncio.gather(*tasks)

                # Update stats
                stats["success"] += sum(results)
                stats["failed"] += len(results) - sum(results)

                # Small delay between batches
                await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"Batch processing error: {e}")

        logger.info(
            f"Batch processing complete: "
            f"{stats['success']}/{stats['total']} succeeded"
        )

        return stats

    async def process_by_ids(self, content_ids: List[int]) -> Dict[str, int]:
        """
        Process specific content items by ID

        Args:
            content_ids: List of content IDs

        Returns:
            Statistics dictionary
        """
        stats = {
            "total": len(content_ids),
            "success": 0,
            "failed": 0
        }

        async with AsyncSessionLocal() as session:
            for content_id in content_ids:
                query = select(Content).where(Content.id == content_id)
                result = await session.execute(query)
                content = result.scalar_one_or_none()

                if content:
                    success = await self.process_content(content)
                    if success:
                        stats["success"] += 1
                    else:
                        stats["failed"] += 1

        return stats

    async def reprocess_all(self) -> Dict[str, int]:
        """
        Reprocess all contents (reset processed flag)

        Returns:
            Statistics dictionary
        """
        logger.info("Reprocessing all contents...")

        async with AsyncSessionLocal() as session:
            # Reset processed flag
            stmt = (
                update(Content)
                .values(is_processed=False)
            )
            await session.execute(stmt)
            await session.commit()

        # Then process
        return await self.process_batch(limit=10000)

    async def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics

        Returns:
            Statistics dictionary
        """
        async with AsyncSessionLocal() as session:
            from sqlalchemy import func

            # Total count
            total_query = select(func.count(Content.id))
            total = await session.scalar(total_query)

            # Processed count
            processed_query = select(func.count(Content.id)).where(
                Content.is_processed == True
            )
            processed = await session.scalar(processed_query)

            # Unprocessed count
            unprocessed = total - processed

            # Count by category
            category_query = (
                select(Content.category, func.count(Content.id))
                .where(Content.is_processed == True)
                .group_by(Content.category)
            )
            category_result = await session.execute(category_query)
            by_category = dict(category_result.all())

            return {
                "total": total,
                "processed": processed,
                "unprocessed": unprocessed,
                "progress": (processed / total * 100) if total > 0 else 0,
                "by_category": by_category,
                "embedding_dim": self.embedding_service.embedding_dim
            }


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="NLP Processor")
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of contents to process"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Batch size for processing"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics only"
    )
    parser.add_argument(
        "--reprocess-all",
        action="store_true",
        help="Reprocess all contents"
    )

    args = parser.parse_args()

    # Configure logging
    logger.add(
        "logs/nlp_processor.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO"
    )

    processor = NLPProcessor()

    if args.stats:
        # Show stats only
        stats = await processor.get_processing_stats()
        logger.info("=" * 60)
        logger.info("📊 NLP Processing Statistics")
        logger.info("=" * 60)
        logger.info(f"Total contents: {stats['total']}")
        logger.info(f"Processed: {stats['processed']}")
        logger.info(f"Unprocessed: {stats['unprocessed']}")
        logger.info(f"Progress: {stats['progress']:.1f}%")
        logger.info(f"By category: {stats['by_category']}")
        logger.info(f"Embedding dimension: {stats['embedding_dim']}")

    elif args.reprocess_all:
        # Reprocess all
        stats = await processor.reprocess_all()
        logger.info("=" * 60)
        logger.info("✅ Reprocessing Complete")
        logger.info("=" * 60)
        logger.info(f"Success: {stats['success']}")
        logger.info(f"Failed: {stats['failed']}")

    else:
        # Normal batch processing
        logger.info("=" * 60)
        logger.info("🚀 Starting NLP Processor")
        logger.info("=" * 60)

        stats = await processor.process_batch(
            limit=args.limit,
            batch_size=args.batch_size
        )

        logger.info("=" * 60)
        logger.info("✅ Processing Complete")
        logger.info("=" * 60)
        logger.info(f"Total: {stats['total']}")
        logger.info(f"Success: {stats['success']}")
        logger.info(f"Failed: {stats['failed']}")


if __name__ == "__main__":
    asyncio.run(main())
