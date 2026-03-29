"""
Test arXiv crawler
"""
import asyncio
import sys
from pathlib import Path

# Add paths - fix imports
api_path = Path(__file__).parent.parent / "api"
crawler_path = Path(__file__).parent
sys.path.insert(0, str(api_path))
sys.path.insert(0, str(crawler_path))

# Now import from crawler package
import os
os.chdir(crawler_path)

from services.arxiv_service import ArxivAPIService
from services.database_service import DatabaseService
from loguru import logger


async def test_arxiv_api():
    """Test arXiv API service"""
    logger.info("=" * 60)
    logger.info("Testing arXiv API Service")
    logger.info("=" * 60)

    async with ArxivAPIService() as arxiv:
        # Test 1: Fetch recent AI papers
        logger.info("\n📰 Test 1: Fetch recent AI papers (last 7 days)")
        papers = await arxiv.fetch_recent_papers(days=7, max_results=10)

        if papers:
            logger.success(f"✅ Successfully fetched {len(papers)} papers")

            # Display sample paper
            paper = papers[0]
            logger.info(f"\n📄 Sample Paper:")
            logger.info(f"  ID: {paper.id}")
            logger.info(f"  Title: {paper.title[:80]}...")
            logger.info(f"  Authors: {', '.join(paper.authors[:3])}")
            logger.info(f"  Categories: {', '.join(paper.categories[:3])}")
            logger.info(f"  Published: {paper.published_at}")
            logger.info(f"  URL: {paper.arxiv_url}")
        else:
            logger.warning("⚠️  No papers fetched")

        # Test 2: Search by keyword
        logger.info("\n🔍 Test 2: Search by keyword")
        papers = await arxiv.fetch_papers(
            query="GPT-4",
            max_results=5
        )

        if papers:
            logger.success(f"✅ Found {len(papers)} papers about 'GPT-4'")
            for i, paper in enumerate(papers[:3], 1):
                logger.info(f"  {i}. {paper.title[:60]}...")
        else:
            logger.warning("⚠️  No papers found")

        # Test 3: Fetch by ID
        logger.info("\n🎯 Test 3: Fetch by ID")
        if papers:
            paper = await arxiv.fetch_by_id(papers[0].id)
            if paper:
                logger.success(f"✅ Successfully fetched paper {paper.id}")
            else:
                logger.warning("⚠️  Failed to fetch paper by ID")


async def test_database_storage():
    """Test database storage"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Database Storage")
    logger.info("=" * 60)

    db_service = DatabaseService()

    # Get current stats
    logger.info("\n📊 Current Database Stats:")
    stats = await db_service.get_stats()
    logger.info(f"  Total papers: {stats['total']}")
    logger.info(f"  Processed: {stats['processed']}")
    logger.info(f"  Unprocessed: {stats['unprocessed']}")
    logger.info(f"  By source: {stats['by_source']}")

    # Fetch and store some papers
    logger.info("\n💾 Fetching and storing papers...")
    async with ArxivAPIService() as arxiv:
        papers = await arxiv.fetch_recent_papers(days=1, max_results=20)

        if papers:
            stored_count = await db_service.store_papers_batch(papers)
            logger.success(f"✅ Stored {stored_count}/{len(papers)} papers")

    # Get updated stats
    logger.info("\n📊 Updated Database Stats:")
    stats = await db_service.get_stats()
    logger.info(f"  Total papers: {stats['total']}")
    logger.info(f"  Processed: {stats['processed']}")
    logger.info(f"  Unprocessed: {stats['unprocessed']}")


async def main():
    """Run all tests"""
    try:
        await test_arxiv_api()
        await test_database_storage()

        logger.success("\n" + "=" * 60)
        logger.success("✅ All tests completed successfully!")
        logger.success("=" * 60)

    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
