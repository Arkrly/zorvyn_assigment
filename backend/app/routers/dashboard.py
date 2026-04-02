"""Dashboard API router with analytics endpoints."""
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.dashboard.aggregations import (
    get_category_totals,
    get_monthly_trends,
    get_recent_transactions,
    get_summary,
)
from app.db.session import get_db
from app.models.user import User

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_summary_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get financial summary: total income, expenses, net balance, and transaction count.
    
    Returns user-specific financial summary filtered by authentication.
    """
    return await get_summary(db, str(current_user.id))


@router.get("/categories")
async def get_categories_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    type: str | None = Query(None, description="Filter by type: income or expense"),
) -> list[dict[str, Any]]:
    """
    Get totals grouped by category.
    
    Optionally filter by transaction type (income or expense).
    """
    return await get_category_totals(db, str(current_user.id), type)


@router.get("/trends")
async def get_trends_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    months: int = Query(12, ge=1, le=24, description="Number of months to include"),
) -> list[dict[str, Any]]:
    """
    Get monthly income and expense trends.
    
    Returns monthly breakdown for the specified number of months.
    """
    return await get_monthly_trends(db, str(current_user.id), months)


@router.get("/recent")
async def get_recent_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50, description="Number of transactions to return"),
) -> list[dict[str, Any]]:
    """
    Get recent transactions.
    
    Returns most recent transactions ordered by date descending.
    """
    return await get_recent_transactions(db, str(current_user.id), limit)