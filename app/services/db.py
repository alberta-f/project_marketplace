from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import config

engine = create_async_engine(config.database.url, echo=True)

async_session_maker = sessionmaker(
    bind=engine,
    expire_on_commit=True,
    class_=AsyncSession
)


async def get_db_session():
    async with async_session_maker() as session:
        yield session
