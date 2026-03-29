"""
arXiv Crawler Scheduler
Manages periodic crawling of arXiv papers
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from services.arxiv_service import ArxivAPIService, ArxivPaper
from services.database_service import DatabaseService


class ArxivScheduler:
    """
    Scheduler for periodic arXiv crawling
    """

    def __init__(
        self,
        interval_minutes: int = 30,
        max_papers_per_run: int = 200
    ):
        """
        Initialize scheduler

        Args:
            interval_minutes: Interval between crawl runs in minutes
            max_papers_per_run: Maximum papers to fetch per run
        """
        self.interval_minutes = interval_minutes
        self.max_papers_per_run = max_papers_per_run
        self.scheduler = AsyncIOScheduler()
        self.db_service = DatabaseService()
        self.is_running = False

    async def crawl_task(self):
        """
        Execute a single crawl task
        """
        if self.is_running:
            logger.warning("Previous crawl still running, skipping...")
            return

        self.is_running = True
        start_time = datetime.now()

        try:
            logger.info("🕷️  Starting arXiv crawl task...")

            async with ArxivAPIService() as arxiv_service:
                # Fetch recent papers
                papers = await arxiv_service.fetch_recent_papers(
                    days=1,  # Last 24 hours
                    max_results=self.max_papers_per_run
                )

                logger.info(f"Found {len(papers)} papers")

                # Store in database
                stored_count = await self.db_service.store_papers_batch(papers)

                # Get stats
                stats = await self.db_service.get_stats()

            elapsed = (datetime.now() - start_time).total_seconds()

            logger.info(
                f"✅ Crawl completed in {elapsed:.1f}s - "
                f"Stored {stored_count} papers - "
                f"Total in DB: {stats['total']}"
            )

        except Exception as e:
            logger.error(f"❌ Crawl task failed: {e}")

        finally:
            self.is_running = False

    async def start(self):
        """
        Start the scheduler
        """
        logger.info(f"🚀 Starting arXiv scheduler (interval: {self.interval_minutes} minutes)")

        # Run initial crawl immediately
        await self.crawl_task()

        # Schedule periodic crawling
        self.scheduler.add_job(
            self.crawl_task,
            IntervalTrigger(minutes=self.interval_minutes),
            id="arxiv_crawler",
            name="arXiv Paper Crawler",
            max_instances=1,
            coalesce=True
        )

        self.scheduler.start()
        logger.info("✅ Scheduler started")

    async def stop(self):
        """
        Stop the scheduler
        """
        logger.info("🛑 Stopping scheduler...")
        self.scheduler.shutdown(wait=True)
        logger.info("✅ Scheduler stopped")

    def get_next_run_time(self) -> Optional[datetime]:
        """
        Get next scheduled run time

        Returns:
            Next run datetime or None
        """
        job = self.scheduler.get_job("arxiv_crawler")
        return job.next_run_time if job else None


async def run_once():
    """
    Run crawler once (for testing)
    """
    logger.info("Running arXiv crawler once...")

    async with ArxivAPIService() as arxiv_service:
        # Fetch recent papers
        papers = await arxiv_service.fetch_recent_papers(
            days=1,
            max_results=100
        )

        logger.info(f"Found {len(papers)} papers")

        # Store in database
        db_service = DatabaseService()
        stored_count = await db_service.store_papers_batch(papers)

        # Get stats
        stats = await db_service.get_stats()

        logger.info(f"✅ Stored {stored_count} papers")
        logger.info(f"Total in database: {stats['total']}")
        logger.info(f"Unprocessed: {stats['unprocessed']}")

        return papers


async def main():
    """
    Main entry point
    """
    import argparse

    parser = argparse.ArgumentParser(description="arXiv Crawler")
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Crawl interval in minutes"
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=200,
        help="Maximum papers per run"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit"
    )

    args = parser.parse_args()

    # Configure logging
    logger.add(
        "logs/crawler.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO"
    )

    if args.once:
        # Run once
        await run_once()
    else:
        # Run scheduler
        scheduler = ArxivScheduler(
            interval_minutes=args.interval,
            max_papers_per_run=args.max_papers
        )

        try:
            await scheduler.start()

            # Keep running
            while True:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            await scheduler.stop()


if __name__ == "__main__":
    asyncio.run(main())
