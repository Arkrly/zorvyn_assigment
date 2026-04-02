"""Transaction service layer with business logic."""
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.models.user import User
from app.auth.deps import Role
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.db.utils import PaginatedResponse, paginate


async def create_transaction(
    db: AsyncSession,
    transaction_data: TransactionCreate,
    current_user: User,
) -> Transaction:
    """
    Create a new transaction.

    Sets user_id to the current user's ID.
    Populates created_by and updated_by with current user's ID.
    """
    transaction = Transaction(
        user_id=current_user.id,
        type=transaction_data.type.value,
        amount=transaction_data.amount,
        category=transaction_data.category,
        description=transaction_data.description,
        date=transaction_data.date,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


async def get_transaction(
    db: AsyncSession,
    transaction_id: str,
    current_user: User,
) -> Optional[Transaction]:
    """
    Get a transaction by ID.

    For VIEWER role: returns None if transaction doesn't belong to user (triggers 404).
    For ANALYST/ADMIN: returns any transaction.
    """
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        return None

    # Ownership check for VIEWER role
    if current_user.role == Role.VIEWER and transaction.user_id != current_user.id:
        return None  # Return None to trigger 404

    return transaction


async def update_transaction(
    db: AsyncSession,
    transaction: Transaction,
    transaction_data: TransactionUpdate,
    current_user: User,
) -> Transaction:
    """
    Update an existing transaction.

    Updates only provided fields.
    Always sets updated_by to current user's ID.
    """
    if transaction_data.type is not None:
        transaction.type = transaction_data.type.value
    if transaction_data.amount is not None:
        transaction.amount = transaction_data.amount
    if transaction_data.category is not None:
        transaction.category = transaction_data.category
    if transaction_data.description is not None:
        transaction.description = transaction_data.description
    if transaction_data.date is not None:
        transaction.date = transaction_data.date

    # Always update audit field
    transaction.updated_by = current_user.id

    await db.commit()
    await db.refresh(transaction)
    return transaction


async def delete_transaction(
    db: AsyncSession,
    transaction: Transaction,
    current_user: User,
) -> None:
    """
    Soft delete a transaction.

    Sets is_deleted = True.
    Sets updated_by to current user's ID.
    """
    transaction.is_deleted = True
    transaction.updated_by = current_user.id
    await db.commit()


async def list_transactions(
    db: AsyncSession,
    current_user: User,
    type_filter: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    sort_by: str = "date",
    order: str = "asc",
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[Transaction]:
    """
    List transactions with role-based filtering, pagination, and sorting.

    VIEWER: sees only own transactions (filtered by user_id).
    ANALYST/ADMIN: sees all transactions (no filter).
    """
    # Build base query
    query = select(Transaction)

    # Ownership filter - VIEWER sees only own transactions
    if current_user.role == Role.VIEWER:
        query = query.where(Transaction.user_id == current_user.id)
    # ANALYST/ADMIN see all (no additional filter)

    # Apply filters
    if type_filter:
        query = query.where(Transaction.type == type_filter)
    if date_from:
        query = query.where(Transaction.date >= date_from)
    if date_to:
        query = query.where(Transaction.date <= date_to)

    # Apply sorting
    sort_column = Transaction.date if sort_by == "date" else Transaction.amount
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Use pagination utility
    return await paginate(db, query, page, page_size)