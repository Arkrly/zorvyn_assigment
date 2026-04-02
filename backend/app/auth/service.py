"""JWT token creation and validation service."""
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.refresh_token import RefreshToken


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create JWT access token with configurable expiry.

    Args:
        data: Dict containing claims (sub, email, role, etc.)
        expires_delta: Optional custom expiry. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        Encoded JWT string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def create_refresh_token(db: AsyncSession, user_id: str) -> tuple[str, RefreshToken]:
    """
    Create and store refresh token.

    Args:
        db: Database session
        user_id: User ID to associate with the token

    Returns:
        Tuple of (raw_token_string, RefreshToken_db_object)
    """
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    db_token = RefreshToken(
        id=str(uuid.uuid4()),
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)

    return token, db_token


async def verify_refresh_token(db: AsyncSession, token: str) -> RefreshToken | None:
    """
    Verify refresh token, return DB object if valid.

    Args:
        db: Database session
        token: Raw refresh token string

    Returns:
        RefreshToken object if valid, None otherwise
    """
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none()


async def rotate_refresh_token(db: AsyncSession, old_token: str) -> tuple[str, RefreshToken]:
    """
    Rotate refresh token: verify old token, delete it, create new one.

    Args:
        db: Database session
        old_token: Raw refresh token to rotate

    Returns:
        Tuple of (new_raw_token, new_RefreshToken_db_object)

    Raises:
        HTTPException: If old token is invalid or expired
    """
    # Verify old token
    old_db_token = await verify_refresh_token(db, old_token)
    if not old_db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Delete old token (rotation)
    await db.delete(old_db_token)

    # Create new token for the same user
    new_token, new_db_token = await create_refresh_token(db, old_db_token.user_id)

    return new_token, new_db_token