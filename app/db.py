from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL

# Async engine for PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# Dependency to get async session
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
