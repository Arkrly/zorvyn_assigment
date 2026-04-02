"""Authentication module exports."""
from app.auth.service import create_access_token
from app.auth.router import router
from app.auth.deps import get_current_user, require_role, CurrentUser, Role
from app.auth.schemas import Token, UserCreate, UserResponse, RefreshRequest
from app.core.security import hash_password, verify_password, password_hash, DUMMY_HASH

__all__ = [
    "router",
    "create_access_token",
    "get_current_user",
    "require_role",
    "CurrentUser",
    "Role",
    "Token",
    "UserCreate",
    "UserResponse",
    "RefreshRequest",
    "hash_password",
    "verify_password",
    "password_hash",
    "DUMMY_HASH",
]