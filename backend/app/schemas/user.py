"""User Pydantic schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    VIEWER = "VIEWER"
    ANALYST = "ANALYST"
    ADMIN = "ADMIN"


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    email: str
    name: Optional[str]
    role: str
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[str]

    model_config = {"from_attributes": True}


class UserList(BaseModel):
    """Schema for paginated user list."""
    items: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int