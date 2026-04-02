"""Transaction Pydantic schemas."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class TransactionType(str, Enum):
    """Transaction type enumeration."""
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class TransactionCreate(BaseModel):
    """Schema for creating a new transaction."""
    type: TransactionType
    amount: Decimal = Field(..., ge=0, max_digits=12, decimal_places=2)
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    date: datetime

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category is not empty."""
        if not v or not v.strip():
            raise ValueError("Category cannot be empty")
        return v.strip()


class TransactionUpdate(BaseModel):
    """Schema for updating an existing transaction."""
    type: Optional[TransactionType] = None
    amount: Optional[Decimal] = Field(None, ge=0, max_digits=12, decimal_places=2)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    date: Optional[datetime] = None


class TransactionResponse(BaseModel):
    """Schema for transaction response."""
    id: str
    user_id: str
    type: str
    amount: Decimal
    category: str
    description: Optional[str]
    date: datetime
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]

    model_config = {"from_attributes": True}


class TransactionList(BaseModel):
    """Schema for paginated transaction list."""
    items: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int