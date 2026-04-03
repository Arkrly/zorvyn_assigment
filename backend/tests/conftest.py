"""Pytest configuration - use SQLite file database"""
import pytest
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.db.session import get_db, AsyncSessionLocal
from app.core.config import settings


@pytest.fixture(scope="function")
def client():
    """Create test client with test database."""
    # Patch settings to use test database
    test_db_url = "sqlite+aiosqlite:///./test_temp.db"
    original_db_url = settings.DATABASE_URL
    
    # Create test engine
    engine = create_async_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Override the global session maker
    global AsyncSessionLocal
    test_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    AsyncSessionLocal = test_session_maker
    
    # Create tables
    from sqlalchemy.ext.asyncio import AsyncEngine
    # Need sync engine for create_all
    sync_engine = create_async_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
    )
    import asyncio
    asyncio.run(sync_engine.begin().__aenter__())
    Base.metadata.create_all(bind=sync_engine.sync_engine)
    
    # Create override function
    async def override_get_db():
        async with test_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    
    from fastapi.testclient import TestClient
    tc = TestClient(app)
    
    yield tc
    
    # Cleanup
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=sync_engine.sync_engine)
    asyncio.run(sync_engine.dispose())
    asyncio.run(engine.dispose())
    
    # Restore original
    AsyncSessionLocal = None
    if os.path.exists("./test_temp.db"):
        os.remove("./test_temp.db")