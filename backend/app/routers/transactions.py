"""Transaction router with CRUD endpoints."""
from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user, require_role, Role
from app.db.session import get_db
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionList,
)
from app.services.transaction import (
    create_transaction,
    get_transaction,
    update_transaction,
    delete_transaction,
    list_transactions,
)

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.get("", response_model=TransactionList)
async def list_transactions_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    type: Optional[str] = Query(None, description="INCOME or EXPENSE"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    sort_by: str = Query("date", description="date or amount"),
    order: str = Query("asc", description="asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> TransactionList:
    """
    List transactions with filtering, pagination, and sorting.

    - VIEWER: sees only own transactions
    - ANALYST/ADMIN: sees all transactions
    """
    return await list_transactions(
        db=db,
        current_user=current_user,
        type_filter=type,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_endpoint(
    transaction_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TransactionResponse:
    """Get a transaction by ID with ownership check."""
    transaction = await get_transaction(db, transaction_id, current_user)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return transaction


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction_endpoint(
    transaction_data: TransactionCreate,
    current_user: Annotated[User, Depends(require_role(Role.ANALYST, Role.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TransactionResponse:
    """Create a new transaction (ANALYST/ADMIN only)."""
    transaction = await create_transaction(db, transaction_data, current_user)
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction_endpoint(
    transaction_id: str,
    transaction_data: TransactionUpdate,
    current_user: Annotated[User, Depends(require_role(Role.ANALYST, Role.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TransactionResponse:
    """Update a transaction (ANALYST/ADMIN only)."""
    transaction = await get_transaction(db, transaction_id, current_user)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    transaction = await update_transaction(db, transaction, transaction_data, current_user)
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction_endpoint(
    transaction_id: str,
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Soft delete a transaction (ADMIN only)."""
    transaction = await get_transaction(db, transaction_id, current_user)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    await delete_transaction(db, transaction, current_user)