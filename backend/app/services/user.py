"""User service layer with business logic."""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserUpdate


async def list_users(
    db: AsyncSession,
    is_active_filter: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """
    List all users (admin functionality).

    Note: Does NOT apply global soft delete filter - admin needs visibility.
    Optionally filters by is_active.
    Returns paginated response.
    """
    # Build base query
    query = select(User)

    # Apply is_active filter if provided
    if is_active_filter is not None:
        query = query.where(User.is_active == is_active_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return {
        "items": users,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


async def get_user(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get a user by ID."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def update_user(
    db: AsyncSession,
    user: User,
    user_data: UserUpdate,
    current_user: User,
) -> User:
    """
    Update a user.

    If role provided: update user role.
    If is_active provided: update user active status.
    Always sets updated_by to current user's ID.
    """
    if user_data.role is not None:
        user.role = user_data.role.value
    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    # Always update audit field
    user.updated_by = current_user.id

    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(
    db: AsyncSession,
    user: User,
    current_user: User,
) -> None:
    """
    Deactivate a user (soft delete via is_active).

    Sets is_active = False (NOT is_deleted).
    Sets updated_by to current user's ID.
    """
    user.is_active = False
    user.updated_by = current_user.id
    await db.commit()