"""
Content related router
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, ConfigDict

from core.database import get_async_db
from models.models import Content

router = APIRouter()


# Pydanticモデル
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


@router.get("", response_model=ContentListResponse)
async def get_contents(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Category filter"),
    source: Optional[str] = Query(None, description="Source filter"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get content list

    Args:
        page: Page number
        size: Items per page
        category: Category filter
        source: Source filter
        db: Database session

    Returns:
        Content list
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

    # Build response
    return ContentListResponse(
        items=[ContentResponse.model_validate(c) for c in contents],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Get content details

    Args:
        content_id: Content ID
        db: Database session

    Returns:
        Content details

    Raises:
        HTTPException: Content not found
    """
    # Fetch data
    query = select(Content).where(Content.id == content_id)
    result = await db.execute(query)
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Increment view count
    content.view_count += 1
    await db.commit()

    return ContentResponse.model_validate(content)
