"""Authentication request/response schemas."""
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    """User registration request schema."""
    email: EmailStr
    password: str  # Min 8 chars (validated at endpoint level if needed)
    name: str | None = None


class UserResponse(BaseModel):
    """User response schema."""
    id: str
    email: str
    name: str | None
    role: str

    model_config = {"from_attributes": True}


class RefreshRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str