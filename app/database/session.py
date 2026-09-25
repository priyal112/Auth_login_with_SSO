from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


# Create the SQLAlchemy engine
# The engine manages the connection between our FastAPI application and PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)


# Create a session factory
# Each request that needs the database can get its own
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session to FastAPI endpoints

    FastAPI will call this function whenever an endpoint
    uses Depends(get_db_session)
    """

    async with AsyncSessionLocal() as session:
        yield session

