"""Database utility functions."""
from typing import Generic, List, TypeVar
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


async def paginate(
    db: AsyncSession,
    query,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse:
    """
    Paginate a SQLAlchemy async query.

    Validates: page >= 1, 1 <= page_size <= 100
    Returns: PaginatedResponse with items, total, page, page_size, total_pages
    Handles edge case: total=0 returns total_pages=0
    """
    # Validate bounds
    page = max(1, page)
    page_size = min(100, max(1, page_size))
    offset = (page - 1) * page_size

    # Get total count - use a simpler approach
    # Count directly without subquery for better compatibility
    count_result = await db.execute(func.count(query.selected_columns[0]))
    total = count_result.scalar() or 0

    # Get paginated items
    paginated_query = query.offset(offset).limit(page_size)
    result = await db.execute(paginated_query)
    items = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )