from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.models.base import (
    Base,
)
from app.utils.settings import settings

engine = create_async_engine(
    settings.get_database_url(),
    echo=settings.fastapi_debug,
    future=True,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting an async database session.
    Auto-commits when no exception is raised and auto-rollbacks on exceptions

    ```python
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db_session)):
            ...
    ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    await engine.dispose()
