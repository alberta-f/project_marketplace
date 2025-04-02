from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config_file import config

engine = create_async_engine(config.database.url, echo=True)

async_session_maker = sessionmaker(
    bind=engine,
    expire_on_commit=True,
    class_=AsyncSession
)

Base = DeclarativeBase()

async def get_db():
    async with async_session_maker() as session:
        yield session
