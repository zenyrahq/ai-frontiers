"""
arXiv API Service
Handles communication with arXiv API for paper fetching
"""
import asyncio
import aiohttp
import feedparser
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from loguru import logger
from dataclasses import dataclass
import xml.etree.ElementTree as ET


@dataclass
class ArxivPaper:
    """Data model for arXiv paper"""
    id: str
    title: str
    abstract: str
    authors: List[str]
    categories: List[str]
    published_at: datetime
    updated_at: datetime
    arxiv_url: str
    pdf_url: str
    comment: Optional[str] = None
    journal_ref: Optional[str] = None
    doi: Optional[str] = None
    primary_category: Optional[str] = None


class ArxivAPIService:
    """
    arXiv API Service

    Official API documentation: https://arxiv.org/help/api/user-manual
    """

    BASE_URL = "http://export.arxiv.org/api/query"

    # AI-related categories
    AI_CATEGORIES = [
        "cs.AI",   # Artificial Intelligence
        "cs.LG",   # Machine Learning
        "cs.CL",   # Computation and Language
        "cs.CV",   # Computer Vision and Pattern Recognition
        "cs.NE",   # Neural and Evolutionary Computing
        "cs.RO",   # Robotics
        "stat.ML", # Machine Learning (Statistics)
    ]

    def __init__(self, max_retries: int = 3, retry_delay: int = 3):
        """
        Initialize arXiv API service

        Args:
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_papers(
        self,
        query: Optional[str] = None,
        categories: Optional[List[str]] = None,
        max_results: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: str = "submittedDate",
        sort_order: str = "descending"
    ) -> List[ArxivPaper]:
        """
        Fetch papers from arXiv API

        Args:
            query: Search query (e.g., "deep learning")
            categories: List of arXiv categories (e.g., ["cs.AI", "cs.LG"])
            max_results: Maximum number of results to fetch
            start_date: Filter papers published after this date
            end_date: Filter papers published before this date
            sort_by: Sort field (relevance, lastUpdatedDate, submittedDate)
            sort_order: Sort order (ascending, descending)

        Returns:
            List of ArxivPaper objects
        """
        # Build search query
        search_query = self._build_search_query(query, categories)

        # Build request parameters
        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }

        # Fetch with retry logic
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching papers from arXiv (attempt {attempt + 1}/{self.max_retries})")
                logger.info(f"Query: {search_query}")

                async with self.session.get(self.BASE_URL, params=params) as response:
                    if response.status == 200:
                        content = await response.text()
                        papers = self._parse_response(content)

                        # Filter by date if specified
                        if start_date or end_date:
                            papers = self._filter_by_date(papers, start_date, end_date)

                        logger.info(f"Successfully fetched {len(papers)} papers")
                        return papers
                    else:
                        logger.warning(f"arXiv API returned status {response.status}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay)

            except Exception as e:
                logger.error(f"Error fetching papers (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)

        logger.error("Failed to fetch papers after all retries")
        return []

    def _build_search_query(
        self,
        query: Optional[str],
        categories: Optional[List[str]]
    ) -> str:
        """
        Build arXiv search query string

        Args:
            query: Text search query
            categories: Category filters

        Returns:
            Formatted search query string
        """
        parts = []

        # Add category filter
        if categories:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            parts.append(f"({cat_query})")
        else:
            # Default to AI categories
            cat_query = " OR ".join([f"cat:{cat}" for cat in self.AI_CATEGORIES])
            parts.append(f"({cat_query})")

        # Add text query
        if query:
            parts.append(f"all:{query}")

        return " AND ".join(parts) if len(parts) > 1 else parts[0]

    def _parse_response(self, xml_content: str) -> List[ArxivPaper]:
        """
        Parse arXiv API XML response

        Args:
            xml_content: XML response from arXiv API

        Returns:
            List of ArxivPaper objects
        """
        papers = []
        feed = feedparser.parse(xml_content)

        for entry in feed.entries:
            try:
                # Extract paper ID from URL
                arxiv_url = entry.id
                paper_id = arxiv_url.split("/")[-1]

                # Extract authors
                authors = [author.name for author in entry.authors]

                # Extract categories
                categories = [tag.term for tag in entry.tags] if hasattr(entry, "tags") else []

                # Parse dates
                published_at = datetime(*entry.published_parsed[:6])
                updated_at = datetime(*entry.updated_parsed[:6])

                # Build PDF URL
                pdf_url = arxiv_url.replace("/abs/", "/pdf/") + ".pdf"

                paper = ArxivPaper(
                    id=paper_id,
                    title=entry.title.strip().replace("\n", " "),
                    abstract=entry.summary.strip().replace("\n", " "),
                    authors=authors,
                    categories=categories,
                    published_at=published_at,
                    updated_at=updated_at,
                    arxiv_url=arxiv_url,
                    pdf_url=pdf_url,
                    comment=entry.get("arxiv_comment"),
                    journal_ref=entry.get("arxiv_journal_ref"),
                    doi=entry.get("arxiv_doi"),
                    primary_category=entry.get("arxiv_primary_category", {}).get("term")
                )

                papers.append(paper)

            except Exception as e:
                logger.error(f"Error parsing paper entry: {e}")
                continue

        return papers

    def _filter_by_date(
        self,
        papers: List[ArxivPaper],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[ArxivPaper]:
        """
        Filter papers by publication date

        Args:
            papers: List of papers
            start_date: Start date filter
            end_date: End date filter

        Returns:
            Filtered list of papers
        """
        filtered = []

        for paper in papers:
            if start_date and paper.published_at < start_date:
                continue
            if end_date and paper.published_at > end_date:
                continue
            filtered.append(paper)

        return filtered

    async def fetch_by_id(self, paper_id: str) -> Optional[ArxivPaper]:
        """
        Fetch a single paper by arXiv ID

        Args:
            paper_id: arXiv paper ID (e.g., "2301.07041")

        Returns:
            ArxivPaper object or None
        """
        papers = await self.fetch_papers(
            query=f"id:{paper_id}",
            max_results=1
        )
        return papers[0] if papers else None

    async def fetch_recent_papers(
        self,
        days: int = 7,
        categories: Optional[List[str]] = None,
        max_results: int = 500
    ) -> List[ArxivPaper]:
        """
        Fetch recent papers from the last N days

        Args:
            days: Number of days to look back
            categories: Category filters
            max_results: Maximum results

        Returns:
            List of recent papers
        """
        start_date = datetime.now() - timedelta(days=days)

        return await self.fetch_papers(
            categories=categories,
            max_results=max_results,
            start_date=start_date,
            sort_by="submittedDate",
            sort_order="descending"
        )
