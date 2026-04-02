"""User management router with admin endpoints."""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user, require_role, Role
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse, UserList
from app.services.user import (
    list_users,
    get_user,
    update_user,
    deactivate_user,
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("", response_model=UserList)
async def list_users_endpoint(
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> UserList:
    """List all users (ADMIN only)."""
    result = await list_users(
        db=db,
        is_active_filter=is_active,
        page=page,
        page_size=page_size,
    )
    return result


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(
    user_id: str,
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Get a user by ID (ADMIN only)."""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: str,
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Update user role or status (ADMIN only)."""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = await update_user(db, user, user_data, current_user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user_endpoint(
    user_id: str,
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Deactivate a user (ADMIN only)."""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself",
        )

    await deactivate_user(db, user, current_user)