#!/usr/bin/env python3
"""
arXiv Crawler - Container Compatible Version
"""
import sys
import os

# Setup path for container environment
if os.path.exists("/app/core"):
    sys.path.insert(0, "/app")
else:
    # Local development
    from pathlib import Path
    api_dir = Path(__file__).parent.parent / "api"
    sys.path.insert(0, str(api_dir))

import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict
import aiohttp
from loguru import logger
from core.database import AsyncSessionLocal
from models.models import Content
from sqlalchemy import text


ARXIV_API_URL = "http://export.arxiv.org/api/query"


async def fetch_arxiv_papers(
    categories: List[str] = None,
    max_results: int = 50,
    days: int = 7
) -> List[Dict]:
    """Fetch papers from arXiv API"""
    if categories is None:
        categories = ["cs.AI", "cs.LG", "cs.CL", "cs.CV"]

    cat_query = " OR ".join([f"cat:{c}" for c in categories])
    start_date = datetime.now() - timedelta(days=days)
    date_str = start_date.strftime("%Y%m%d%H%M%S")

    params = {
        "search_query": f"({cat_query}) AND submittedDate:[{date_str} TO now]",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    logger.info(f"Fetching papers from arXiv...")
    logger.info(f"  Query: {cat_query}")
    logger.info(f"  Date range: {start_date.strftime('%Y-%m-%d')} to now")
    logger.info(f"  Max results: {max_results}")

    timeout = aiohttp.ClientTimeout(total=120)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            logger.info("  Connecting...")
            async with session.get(ARXIV_API_URL, params=params) as response:
                if response.status != 200:
                    logger.error(f"API returned status {response.status}")
                    if response.status == 429:
                        logger.warning("Rate limited! Please wait a few minutes and try again.")
                    return []

                xml_content = await response.text()
                logger.info(f"Received response ({len(xml_content)} bytes)")

                papers = parse_arxiv_response(xml_content)
                logger.info(f"Parsed {len(papers)} papers")

                return papers

        except asyncio.TimeoutError:
            logger.error("Request timeout (120s)")
            logger.info("Tip: arXiv API sometimes responds slowly")
            return []
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return []


def parse_arxiv_response(xml_content: str) -> List[Dict]:
    """Parse arXiv API XML response"""
    papers = []

    try:
        root = ET.fromstring(xml_content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            title_text = title.text.strip() if title is not None else ""

            summary = entry.find("atom:summary", ns)
            summary_text = summary.text.strip() if summary is not None else ""

            id_elem = entry.find("atom:id", ns)
            arxiv_url = id_elem.text if id_elem is not None else ""

            published = entry.find("atom:published", ns)
            pub_date = None
            if published is not None:
                try:
                    pub_date = datetime.fromisoformat(published.text.replace("Z", "+00:00"))
                except:
                    pass

            categories = []
            for cat in entry.findall("atom:category", ns):
                term = cat.get("term")
                if term:
                    categories.append(term)

            authors = []
            for author in entry.findall("atom:author", ns):
                name = author.find("atom:name", ns)
                if name is not None:
                    authors.append(name.text)

            system_category = map_category(categories)

            paper = {
                "title": title_text,
                "summary": summary_text,
                "arxiv_url": arxiv_url,
                "published_at": pub_date,
                "categories": categories,
                "authors": authors,
                "category": system_category,
                "tags": categories[:3] if categories else [],
            }
            papers.append(paper)

    except ET.ParseError as e:
        logger.error(f"XML parse error: {e}")
    except Exception as e:
        logger.error(f"Parse failed: {e}")

    return papers


def map_category(arxiv_categories: List[str]) -> str:
    """Map arXiv categories to system categories"""
    category_map = {
        "cs.AI": "machine_learning",
        "cs.LG": "machine_learning",
        "cs.CL": "natural_language",
        "cs.CV": "computer_vision",
        "cs.RO": "robotics",
        "cs.NE": "deep_learning",
    }

    for cat in arxiv_categories:
        if cat in category_map:
            return category_map[cat]

    return "other"


async def save_papers_to_db(papers: List[Dict]) -> int:
    """Save papers to database"""
    if not papers:
        return 0

    saved = 0

    async with AsyncSessionLocal() as session:
        for paper in papers:
            try:
                result = await session.execute(
                    text("SELECT id FROM contents WHERE original_url = :url"),
                    {"url": paper["arxiv_url"]}
                )
                if result.fetchone():
                    continue

                content = Content(
                    title=paper["title"][:500],
                    summary=paper["summary"][:1000] if paper["summary"] else None,
                    content=paper["summary"],
                    original_url=paper["arxiv_url"],
                    source="arxiv",
                    category=paper["category"],
                    tags=paper["tags"],
                    published_at=paper["published_at"],
                    is_processed=False,
                    view_count=0,
                    like_count=0,
                )
                session.add(content)
                saved += 1

            except Exception as e:
                logger.warning(f"Failed to save paper: {e}")
                continue

        await session.commit()

    return saved


async def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("arXiv Crawler Started")
    logger.info("=" * 60)

    papers = await fetch_arxiv_papers(
        categories=["cs.AI", "cs.LG", "cs.CL", "cs.CV"],
        max_results=50,
        days=7
    )

    if papers:
        logger.info(f"\nSample papers fetched:")
        for i, paper in enumerate(papers[:5], 1):
            logger.info(f"  {i}. {paper['title'][:50]}...")
            logger.info(f"     Categories: {', '.join(paper['categories'][:3])}")

        logger.info(f"\nSaving to database...")
        saved = await save_papers_to_db(papers)
        logger.success(f"Successfully saved {saved} new papers")
    else:
        logger.warning("No papers fetched")
        logger.info("\nPossible reasons:")
        logger.info("1. Rate limited (429) - wait a few minutes")
        logger.info("2. Network connection issue")
        logger.info("3. arXiv API temporarily unavailable")

    logger.info("\n" + "=" * 60)
    return len(papers)


if __name__ == "__main__":
    asyncio.run(main())
