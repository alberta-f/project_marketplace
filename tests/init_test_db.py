import asyncio
import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import Base

DATABASE_URL = os.getenv("DATABASE_URL")
test_engine = create_async_engine(DATABASE_URL, echo=True)
test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

async def create_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    if not DATABASE_URL:
        print('DATABASE_URL is not set')

    else:
        print('Connecting to', DATABASE_URL)
        asyncio.run(create_tables())
        print('Tables created')
