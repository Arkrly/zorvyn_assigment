"""SQLAlchemy async session configuration."""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.base import Base


def _exclude_deleted_criteria(entity):
    """Global query filter to exclude soft-deleted records."""
    if hasattr(entity, "is_deleted"):
        return entity.is_deleted == False
    return True


# Use NullPool for SQLite, asyncpg for PostgreSQL
if settings.DATABASE_URL.startswith("sqlite"):
    engine: AsyncEngine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        poolclass=NullPool,
    )
elif "+asyncpg" in settings.DATABASE_URL:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
else:
    # Convert postgresql:// to postgresql+asyncpg://
    async_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        async_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )


# Create async session factory with global soft-delete filter
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()