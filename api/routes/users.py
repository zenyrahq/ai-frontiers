"""
User related router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from core.database import get_async_db
from models.models import User

router = APIRouter()


class UserResponse(BaseModel):
    """User response"""

    id: int
    email: str
    is_active: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update request"""

    preferences: dict = {}


@router.get("/me", response_model=UserResponse)
async def get_current_user(db: AsyncSession = Depends(get_async_db)):
    """
    Get current user information

    Returns:
        User information
    """
    # TODO: Get user ID from JWT authentication
    # Temporarily return mock data
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate, db: AsyncSession = Depends(get_async_db)
):
    """
    Update user settings

    Args:
        update_data: Update data

    Returns:
        Updated user information
    """
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not implemented yet")
