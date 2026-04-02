"""Dashboard aggregation functions for financial analytics."""
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.transaction import Transaction


async def get_summary(db: AsyncSession, user_id: str) -> dict[str, Any]:
    """
    Get financial summary: total income, expenses, net balance, and transaction count.
    
    Returns:
        dict with total_income, total_expenses, net_balance, transaction_count
    """
    # Get total income
    income_result = await db.execute(
        func.sum(Transaction.amount).filter(
            Transaction.user_id == user_id,
            Transaction.type == "income",
            Transaction.is_deleted == False,
        )
    )
    total_income = income_result.scalar() or Decimal("0")

    # Get total expenses
    expense_result = await db.execute(
        func.sum(Transaction.amount).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.is_deleted == False,
        )
    )
    total_expenses = expense_result.scalar() or Decimal("0")

    # Get transaction count
    count_result = await db.execute(
        func.count(Transaction.id).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
        )
    )
    transaction_count = count_result.scalar() or 0

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": total_income - total_expenses,
        "transaction_count": transaction_count,
    }


async def get_category_totals(
    db: AsyncSession,
    user_id: str,
    transaction_type: str | None = None,
) -> list[dict[str, Any]]:
    """
    Get totals grouped by category.
    
    Args:
        db: Database session
        user_id: User ID to filter transactions
        transaction_type: Optional filter - "income" or "expense"
    
    Returns:
        List of dicts: [{category: str, total: Decimal, count: int}, ...]
    """
    query = (
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("count"),
        Transaction.category,
    ).filter(
        Transaction.user_id == user_id,
        Transaction.is_deleted == False,
    )

    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)

    query = query.group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc())

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "category": row.category,
            "total": row.total or Decimal("0"),
            "count": row.count,
        }
        for row in rows
    ]


async def get_monthly_trends(
    db: AsyncSession,
    user_id: str,
    months: int = 12,
) -> list[dict[str, Any]]:
    """
    Get monthly income and expense trends.
    
    Args:
        db: Database session
        user_id: User ID to filter transactions
        months: Number of months to include (default 12)
    
    Returns:
        List of dicts: [{month: str (YYYY-MM), income: Decimal, expenses: Decimal}, ...]
    """
    from datetime import timedelta
    
    # Calculate the start date (months ago from now)
    end_date = datetime.utcnow()
    start_date = end_date.replace(day=1)  # First of current month
    
    # Get income by month
    income_query = (
        func.sum(Transaction.amount).label("income"),
        func.strftime("%Y-%m", Transaction.date).label("month"),
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == "income",
        Transaction.is_deleted == False,
        Transaction.date >= start_date,
    ).group_by(func.strftime("%Y-%m", Transaction.date))

    income_result = await db.execute(income_query)
    income_by_month = {row.month: row.income for row in income_result.all()}

    # Get expenses by month
    expense_query = (
        func.sum(Transaction.amount).label("expenses"),
        func.strftime("%Y-%m", Transaction.date).label("month"),
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense",
        Transaction.is_deleted == False,
        Transaction.date >= start_date,
    ).group_by(func.strftime("%Y-%m", Transaction.date))

    expense_result = await db.execute(expense_query)
    expense_by_month = {row.month: row.expenses for row in expense_result.all()}

    # Combine results
    all_months = sorted(set(income_by_month.keys()) | set(expense_by_month.keys()), reverse=True)[:months]

    trends = []
    for month in sorted(all_months):
        trends.append({
            "month": month,
            "income": income_by_month.get(month, Decimal("0")),
            "expenses": expense_by_month.get(month, Decimal("0")),
        })

    return trends


async def get_recent_transactions(
    db: AsyncSession,
    user_id: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Get recent transactions ordered by date descending.
    
    Args:
        db: Database session
        user_id: User ID to filter transactions
        limit: Maximum number of transactions to return (default 10)
    
    Returns:
        List of transaction dicts with: id, type, amount, category, description, date
    """
    result = await db.execute(
        Transaction.__table__.select()
        .filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
        )
        .order_by(Transaction.date.desc())
        .limit(limit)
    )
    rows = result.fetchall()

    return [
        {
            "id": row.id,
            "type": row.type,
            "amount": row.amount,
            "category": row.category,
            "description": row.description,
            "date": row.date.isoformat() if row.date else None,
        }
        for row in rows
    ]