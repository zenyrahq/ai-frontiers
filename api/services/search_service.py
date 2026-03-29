"""
Search Service
Handles vector similarity search, full-text search, and hybrid search
"""
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.models import Content
from core.database import AsyncSessionLocal
from core.config import settings


class SearchService:
    """
    Search service with multiple search strategies

    Provides:
    1. Vector similarity search (pgvector)
    2. Full-text search (PostgreSQL)
    3. Hybrid search (combined)
    4. Faceted search (filters)
    """

    def __init__(self):
        """Initialize search service"""
        self.default_limit = 20
        self.max_limit = 100
        logger.info("Search service initialized")

    async def vector_search(
        self,
        query_embedding: List[float],
        limit: int = 20,
        threshold: float = 0.5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Content, float]]:
        """
        Vector similarity search using pgvector

        Args:
            query_embedding: Query vector (384 dimensions)
            limit: Maximum results
            threshold: Minimum similarity score (0-1)
            filters: Optional filters (category, source, etc.)

        Returns:
            List of (Content, similarity) tuples
        """
        async with AsyncSessionLocal() as session:
            try:
                # Convert embedding to PostgreSQL array format
                embedding_str = f"[{','.join(map(str, query_embedding))}]"

                # Build base query with cosine similarity
                query = select(
                    Content,
                    text(f"(1 - (embedding <=> '{embedding_str}'::vector)) as similarity")
                ).where(
                    and_(
                        Content.is_processed == True,
                        Content.embedding.isnot(None)
                    )
                )

                # Add filters
                if filters:
                    if filters.get("category"):
                        query = query.where(Content.category == filters["category"])
                    if filters.get("source"):
                        query = query.where(Content.source == filters["source"])
                    if filters.get("tags"):
                        query = query.where(Content.tags.overlap(filters["tags"]))

                # Order by similarity and limit
                query = query.order_by(text("similarity DESC")).limit(limit)

                # Execute
                result = await session.execute(query)
                rows = result.all()

                # Filter by threshold and format results
                results = []
                for row in rows:
                    content = row[0]
                    similarity = float(row[1])
                    if similarity >= threshold:
                        results.append((content, similarity))

                logger.info(f"Vector search found {len(results)} results (threshold: {threshold})")
                return results

            except Exception as e:
                logger.error(f"Vector search error: {e}")
                return []

    async def fulltext_search(
        self,
        query: str,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Content, float]]:
        """
        Full-text search using PostgreSQL

        Args:
            query: Search query string
            limit: Maximum results
            filters: Optional filters

        Returns:
            List of (Content, rank) tuples
        """
        async with AsyncSessionLocal() as session:
            try:
                # Build search vector query
                # Search in title, summary, and tags
                search_query = f"""
                    SELECT
                        c.*,
                        ts_rank_cd(
                            setweight(to_tsvector('english', c.title), 'A') ||
                            setweight(to_tsvector('english', COALESCE(c.summary, '')), 'B'),
                            plainto_tsquery('english', :query)
                        ) as rank
                    FROM contents c
                    WHERE c.is_processed = TRUE
                    AND (
                        to_tsvector('english', c.title) @@ plainto_tsquery('english', :query)
                        OR to_tsvector('english', COALESCE(c.summary, '')) @@ plainto_tsquery('english', :query)
                    )
                """

                # Add filter conditions
                conditions = []
                params = {"query": query, "limit": limit}

                if filters:
                    if filters.get("category"):
                        conditions.append("c.category = :category")
                        params["category"] = filters["category"]
                    if filters.get("source"):
                        conditions.append("c.source = :source")
                        params["source"] = filters["source"]

                if conditions:
                    search_query += " AND " + " AND ".join(conditions)

                # Order by rank and limit
                search_query += " ORDER BY rank DESC LIMIT :limit"

                # Execute raw SQL
                result = await session.execute(text(search_query), params)
                rows = result.all()

                # Format results
                results = []
                for row in rows:
                    # Create Content object from row
                    content = Content(
                        id=row.id,
                        title=row.title,
                        summary=row.summary,
                        original_url=row.original_url,
                        source=row.source,
                        category=row.category,
                        tags=row.tags,
                        published_at=row.published_at,
                        view_count=row.view_count,
                        like_count=row.like_count
                    )
                    rank = float(row.rank)
                    results.append((content, rank))

                logger.info(f"Full-text search found {len(results)} results for query: {query[:50]}")
                return results

            except Exception as e:
                logger.error(f"Full-text search error: {e}")
                return []

    async def hybrid_search(
        self,
        query: str,
        query_embedding: List[float],
        limit: int = 20,
        vector_weight: float = 0.6,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Content, float]]:
        """
        Hybrid search combining vector and full-text search

        Args:
            query: Search query string
            query_embedding: Query vector
            limit: Maximum results
            vector_weight: Weight for vector search (0-1)
            filters: Optional filters

        Returns:
            List of (Content, combined_score) tuples
        """
        try:
            # Run both searches in parallel
            vector_task = self.vector_search(
                query_embedding=query_embedding,
                limit=limit * 2,  # Get more candidates
                threshold=0.3,
                filters=filters
            )

            text_task = self.fulltext_search(
                query=query,
                limit=limit * 2,
                filters=filters
            )

            # Wait for both
            vector_results = await vector_task
            text_results = await text_task

            # Combine and re-rank
            content_scores = {}

            # Add vector results
            for content, similarity in vector_results:
                content_id = content.id
                if content_id not in content_scores:
                    content_scores[content_id] = {
                        "content": content,
                        "vector_score": similarity,
                        "text_score": 0.0
                    }
                else:
                    content_scores[content_id]["vector_score"] = similarity

            # Add text results
            max_text_rank = max([r[1] for r in text_results]) if text_results else 1.0
            for content, rank in text_results:
                content_id = content.id
                normalized_rank = rank / max_text_rank if max_text_rank > 0 else 0

                if content_id not in content_scores:
                    content_scores[content_id] = {
                        "content": content,
                        "vector_score": 0.0,
                        "text_score": normalized_rank
                    }
                else:
                    content_scores[content_id]["text_score"] = normalized_rank

            # Calculate combined scores
            results = []
            text_weight = 1.0 - vector_weight

            for content_id, scores in content_scores.items():
                combined_score = (
                    vector_weight * scores["vector_score"] +
                    text_weight * scores["text_score"]
                )
                results.append((scores["content"], combined_score))

            # Sort by combined score
            results.sort(key=lambda x: x[1], reverse=True)

            # Limit results
            results = results[:limit]

            logger.info(
                f"Hybrid search: {len(vector_results)} vector + "
                f"{len(text_results)} text → {len(results)} combined"
            )

            return results

        except Exception as e:
            logger.error(f"Hybrid search error: {e}")
            return []

    async def search_by_category(
        self,
        category: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Content]:
        """
        Search contents by category

        Args:
            category: Category name
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            List of Content objects
        """
        async with AsyncSessionLocal() as session:
            query = (
                select(Content)
                .where(
                    and_(
                        Content.is_processed == True,
                        Content.category == category
                    )
                )
                .order_by(Content.published_at.desc())
                .offset(offset)
                .limit(limit)
            )

            result = await session.execute(query)
            contents = result.scalars().all()

            logger.info(f"Found {len(contents)} contents in category: {category}")
            return list(contents)

    async def search_by_tags(
        self,
        tags: List[str],
        limit: int = 20,
        match_all: bool = False
    ) -> List[Content]:
        """
        Search contents by tags

        Args:
            tags: List of tags
            limit: Maximum results
            match_all: If True, all tags must match

        Returns:
            List of Content objects
        """
        async with AsyncSessionLocal() as session:
            query = select(Content).where(Content.is_processed == True)

            if match_all:
                # All tags must be present
                query = query.where(Content.tags.contains(tags))
            else:
                # Any tag can match
                query = query.where(Content.tags.overlap(tags))

            query = query.order_by(Content.published_at.desc()).limit(limit)

            result = await session.execute(query)
            contents = result.scalars().all()

            logger.info(f"Found {len(contents)} contents with tags: {tags}")
            return list(contents)

    async def get_popular_contents(
        self,
        days: int = 7,
        limit: int = 20
    ) -> List[Content]:
        """
        Get popular contents in the last N days

        Args:
            days: Number of days to look back
            limit: Maximum results

        Returns:
            List of Content objects
        """
        async with AsyncSessionLocal() as session:
            # Calculate popularity score
            # Score = view_count + (like_count * 2) + recency bonus
            since = datetime.now() - timedelta(days=days)

            query = select(Content).where(
                and_(
                    Content.is_processed == True,
                    Content.published_at >= since
                )
            ).order_by(
                (Content.view_count + Content.like_count * 2).desc()
            ).limit(limit)

            result = await session.execute(query)
            contents = result.scalars().all()

            logger.info(f"Found {len(contents)} popular contents (last {days} days)")
            return list(contents)

    async def get_related_contents(
        self,
        content_id: int,
        limit: int = 10
    ) -> List[Tuple[Content, float]]:
        """
        Get related contents using vector similarity

        Args:
            content_id: Content ID
            limit: Maximum results

        Returns:
            List of (Content, similarity) tuples
        """
        async with AsyncSessionLocal() as session:
            # Get source content's embedding
            query = select(Content).where(Content.id == content_id)
            result = await session.execute(query)
            source_content = result.scalar_one_or_none()

            if not source_content or not source_content.embedding:
                logger.warning(f"Content {content_id} not found or has no embedding")
                return []

            # Search for similar contents
            return await self.vector_search(
                query_embedding=source_content.embedding,
                limit=limit + 1,  # +1 to exclude source
                threshold=0.3
            )

    async def get_search_suggestions(
        self,
        query: str,
        limit: int = 5
    ) -> List[str]:
        """
        Get search suggestions based on partial query

        Args:
            query: Partial search query
            limit: Maximum suggestions

        Returns:
            List of suggestion strings
        """
        async with AsyncSessionLocal() as session:
            # Search for titles containing the query
            query_obj = (
                select(Content.title)
                .where(Content.title.ilike(f"%{query}%"))
                .distinct()
                .limit(limit)
            )

            result = await session.execute(query_obj)
            titles = [row[0] for row in result.all()]

            return titles


# Singleton instance
_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """Get or create search service singleton"""
    global _search_service

    if _search_service is None:
        _search_service = SearchService()

    return _search_service
