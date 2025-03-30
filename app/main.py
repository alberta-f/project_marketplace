from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware import Middleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from app.db.session import get_db_session
from app.middlewares.auth import AuthMiddleware
from app.routes.auth import auth_router

middleware = [
    Middleware(AuthMiddleware)
]
app = FastAPI(middleware=middleware)
main_router = APIRouter()

main_router.include_router(auth_router, prefix='/auth')

@app.get('/ping')
async def ping(db_session: AsyncSession = Depends(get_db_session)):
    result = await db_session.execute(text('SELECT 1'))

    return {"db": result.scalar()}

app.include_router(main_router)
