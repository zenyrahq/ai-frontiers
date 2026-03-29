"""
Content related router with caching support
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, ConfigDict

from core.database import get_async_db
from models.models import Content
from services.cache_service import cache

router = APIRouter()


# Pydantic models
class ContentResponse(BaseModel):
    """Content response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: Optional[str] = None
    source: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    published_at: Optional[datetime] = None
    view_count: int = 0
    like_count: int = 0


class ContentListResponse(BaseModel):
    """Content list response"""

    items: List[ContentResponse]
    total: int
    page: int
    size: int
    pages: int


async def _fetch_contents_from_db(
    db: AsyncSession,
    page: int,
    size: int,
    category: Optional[str],
    source: Optional[str]
) -> dict:
    """
    Fetch contents from database

    Args:
        db: Database session
        page: Page number
        size: Items per page
        category: Category filter
        source: Source filter

    Returns:
        Dictionary with items, total, page, size, pages
    """
    # Build query
    query = select(Content)

    # Filtering
    if category:
        query = query.where(Content.category == category)
    if source:
        query = query.where(Content.source == source)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Pagination
    offset = (page - 1) * size
    query = query.order_by(Content.published_at.desc()).offset(offset).limit(size)

    # Fetch data
    result = await db.execute(query)
    contents = result.scalars().all()

    # Convert to dict for caching
    return {
        "items": [
            {
                "id": c.id,
                "title": c.title,
                "summary": c.summary,
                "source": c.source,
                "category": c.category,
                "tags": c.tags,
                "published_at": c.published_at.isoformat() if c.published_at else None,
                "view_count": c.view_count,
                "like_count": c.like_count,
            }
            for c in contents
        ],
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size if total else 0,
    }


@router.get("", response_model=ContentListResponse)
async def get_contents(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Category filter"),
    source: Optional[str] = Query(None, description="Source filter"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get content list with caching

    Cache strategy:
    - First page cached for 5 minutes
    - Subsequent pages cached for 3 minutes
    - Filtered results cached for 5 minutes

    Args:
        page: Page number
        size: Items per page
        category: Category filter
        source: Source filter
        db: Database session

    Returns:
        Content list
    """
    # Generate cache key
    cache_key = cache._generate_key(
        "contents",
        page=page,
        size=size,
        category=category,
        source=source
    )

    # Determine TTL based on page
    ttl = 300 if page == 1 else 180  # 5 min for first page, 3 min for others

    # Try cache first
    cached_data = await cache.get(cache_key)

    if cached_data is not None:
        # Convert datetime strings back for response
        for item in cached_data["items"]:
            if item["published_at"]:
                item["published_at"] = datetime.fromisoformat(item["published_at"])

        return ContentListResponse(**cached_data)

    # Fetch from database
    data = await _fetch_contents_from_db(db, page, size, category, source)

    # Cache the result
    await cache.set(cache_key, data, ttl=ttl)

    # Convert datetime strings back for response
    for item in data["items"]:
        if item["published_at"]:
            item["published_at"] = datetime.fromisoformat(item["published_at"])

    return ContentListResponse(**data)


@router.get("/popular", response_model=ContentListResponse)
async def get_popular_contents(
    size: int = Query(10, ge=1, le=50, description="Items per page"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get popular contents (by view count) with caching

    Cache strategy:
    - Cached for 15 minutes

    Args:
        size: Items per page
        db: Database session

    Returns:
        Popular content list
    """
    cache_key = f"contents:popular:{size}"

    # Try cache first
    cached_data = await cache.get(cache_key)

    if cached_data is not None:
        for item in cached_data["items"]:
            if item["published_at"]:
                item["published_at"] = datetime.fromisoformat(item["published_at"])

        return ContentListResponse(**cached_data)

    # Fetch from database
    query = (
        select(Content)
        .where(Content.view_count > 0)
        .order_by(Content.view_count.desc())
        .limit(size)
    )

    result = await db.execute(query)
    contents = result.scalars().all()

    # Get total
    total_query = select(func.count()).select_from(Content).where(Content.view_count > 0)
    total = await db.scalar(total_query)

    # Prepare data
    data = {
        "items": [
            {
                "id": c.id,
                "title": c.title,
                "summary": c.summary,
                "source": c.source,
                "category": c.category,
                "tags": c.tags,
                "published_at": c.published_at.isoformat() if c.published_at else None,
                "view_count": c.view_count,
                "like_count": c.like_count,
            }
            for c in contents
        ],
        "total": total,
        "page": 1,
        "size": size,
        "pages": 1,
    }

    # Cache for 15 minutes
    await cache.set(cache_key, data, ttl=900)

    for item in data["items"]:
        if item["published_at"]:
            item["published_at"] = datetime.fromisoformat(item["published_at"])

    return ContentListResponse(**data)


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get content details with caching

    Cache strategy:
    - Cached for 1 hour
    - View count is always updated (not cached)

    Args:
        content_id: Content ID
        db: Database session

    Returns:
        Content details

    Raises:
        HTTPException: Content not found
    """
    cache_key = f"content:detail:{content_id}"

    # Try cache first
    cached_data = await cache.get(cache_key)

    if cached_data is not None:
        # Still increment view count in background
        query = select(Content).where(Content.id == content_id)
        result = await db.execute(query)
        content = result.scalar_one_or_none()

        if content:
            content.view_count += 1
            await db.commit()
            cached_data["view_count"] = content.view_count

        if cached_data["published_at"]:
            cached_data["published_at"] = datetime.fromisoformat(cached_data["published_at"])

        return ContentResponse(**cached_data)

    # Fetch from database
    query = select(Content).where(Content.id == content_id)
    result = await db.execute(query)
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Increment view count
    content.view_count += 1
    await db.commit()

    # Prepare data for caching
    data = {
        "id": content.id,
        "title": content.title,
        "summary": content.summary,
        "source": content.source,
        "category": content.category,
        "tags": content.tags,
        "published_at": content.published_at.isoformat() if content.published_at else None,
        "view_count": content.view_count,
        "like_count": content.like_count,
    }

    # Cache for 1 hour
    await cache.set(cache_key, data, ttl=3600)

    return ContentResponse(**data)


@router.delete("/cache")
async def clear_cache():
    """
    Clear all content cache

    Returns:
        Number of keys deleted
    """
    deleted = await cache.delete_pattern("contents:*")
    deleted += await cache.delete_pattern("content:*")

    return {"message": f"Cleared {deleted} cache keys"}
