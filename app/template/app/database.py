from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.models.utils.utils import Base
from app.utils.settings import settings
from app.utils.logger import logger

logger = logger.getChild("database")

engine = create_async_engine(
    settings.get_database_url(),
    echo=settings.db_engine_debug,
    echo_pool=settings.db_engine_debug,
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
    logger.info("Getting database session")
    async with AsyncSessionLocal() as session:
        try:
            yield session
            logger.info("Committing database session")
            await session.commit()
        except Exception:
            logger.error("Rolling back database session")
            await session.rollback()
            raise
    logger.info("Relinquishing database session")


async def init_db() -> None:
    logger.info(
        "Initializing database", extra={"database": settings.get_database_info_safe()}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


async def close_db() -> None:
    logger.info("Closing database")
    await engine.dispose()
    logger.info("Database closed")
