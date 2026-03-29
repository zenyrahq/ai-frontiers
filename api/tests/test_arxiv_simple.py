#!/usr/bin/env python3
"""
Simple arXiv Crawler Test
"""
import sys
import os
import asyncio
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "api"))
sys.path.insert(0, str(project_root / "crawler"))

# Import after path setup
os.chdir(project_root / "crawler")

import feedparser
import aiohttp
from datetime import datetime, timedelta
from loguru import logger

# Simple arXiv fetcher
ARXIV_API = "http://export.arxiv.org/api/query"
AI_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV"]


async def fetch_papers(max_results=10):
    """Fetch papers from arXiv"""
    # Build query
    cat_query = " OR ".join([f"cat:{cat}" for cat in AI_CATEGORIES])
    params = {
        "search_query": f"({cat_query})",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    logger.info(f"Fetching {max_results} papers from arXiv...")

    async with aiohttp.ClientSession() as session:
        async with session.get(ARXIV_API, params=params) as response:
            if response.status == 200:
                content = await response.text()
                return parse_papers(content)
            else:
                logger.error(f"arXiv API error: {response.status}")
                return []


def parse_papers(xml_content):
    """Parse arXiv XML response"""
    papers = []
    feed = feedparser.parse(xml_content)

    for entry in feed.entries:
        try:
            paper = {
                "id": entry.id.split("/")[-1],
                "title": entry.title.strip().replace("\n", " "),
                "abstract": entry.summary.strip().replace("\n", " ")[:200] + "...",
                "authors": [a.name for a in entry.authors[:3]],
                "categories": [t.term for t in entry.tags] if hasattr(entry, "tags") else [],
                "published": datetime(*entry.published_parsed[:6]),
                "url": entry.id
            }
            papers.append(paper)
        except Exception as e:
            logger.error(f"Error parsing entry: {e}")
            continue

    return papers


async def main():
    """Main test"""
    logger.info("=" * 60)
    logger.info("🧪 arXiv Crawler Test")
    logger.info("=" * 60)

    # Test 1: Fetch recent papers
    logger.info("\n📰 Test 1: Fetch recent papers")
    papers = await fetch_papers(10)

    if papers:
        logger.success(f"✅ Successfully fetched {len(papers)} papers\n")

        for i, paper in enumerate(papers[:5], 1):
            logger.info(f"{i}. {paper['title'][:60]}...")
            logger.info(f"   ID: {paper['id']}")
            logger.info(f"   Authors: {', '.join(paper['authors'])}")
            logger.info(f"   Categories: {', '.join(paper['categories'][:3])}")
            logger.info(f"   Published: {paper['published'].strftime('%Y-%m-%d')}")
            logger.info("")

        logger.success(f"✅ Test passed! Fetched {len(papers)} papers from arXiv")
    else:
        logger.error("❌ Test failed! Could not fetch papers")
        return False

    logger.info("\n" + "=" * 60)
    logger.success("✅ All tests passed!")
    logger.info("=" * 60)

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
