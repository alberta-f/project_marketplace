from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from app.db.session import get_db_session

app = FastAPI()

@app.get('/ping')
async def ping(db_session: AsyncSession = Depends(get_db_session)):
    result = await db_session.execute(text('SELECT 1'))

    return {"db": result.scalar()}
