"""
arXiv Crawler Main Entry Point
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from spiders.arxiv_scheduler import main as run_crawler


def setup_logging():
    """Configure logging"""
    logger.remove()  # Remove default handler

    # Console output
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
              "<level>{level: <8}</level> | "
              "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
              "<level>{message}</level>"
    )

    # File output
    logger.add(
        "logs/crawler.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )


if __name__ == "__main__":
    setup_logging()
    asyncio.run(run_crawler())
