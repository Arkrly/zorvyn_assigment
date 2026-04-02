"""Dashboard module for financial analytics aggregations."""
from app.dashboard.aggregations import (
    get_category_totals,
    get_monthly_trends,
    get_recent_transactions,
    get_summary,
)

__all__ = [
    "get_summary",
    "get_category_totals",
    "get_monthly_trends",
    "get_recent_transactions",
]