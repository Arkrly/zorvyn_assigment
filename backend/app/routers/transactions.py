"""Transaction router with CRUD endpoints."""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user, require_role, Role
from app.db.session import get_db
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
)
from app.services.transaction import (
    create_transaction,
    get_transaction,
    update_transaction,
    delete_transaction,
)

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


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