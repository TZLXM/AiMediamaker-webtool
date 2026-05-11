"""
Pytest fixtures
"""
import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models.base import Base
from app.core.database import async_session_maker

# Use an in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create a test engine with in-memory SQLite."""
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncSession:
    """Create a fresh database session for each test."""
    async with engine.connect() as conn:
        trans = await conn.begin()
        session_maker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        async with session_maker() as session:
            yield session
            await session.rollback()
        await trans.rollback()
