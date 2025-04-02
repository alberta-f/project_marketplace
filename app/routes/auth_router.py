from fastapi import APIRouter

from app.routes.password import register_router
from app.routes.session import session_router

auth_router = APIRouter(prefix='/auth')


auth_router.include_router(register_router)
auth_router.include_router(register_router)
auth_router.include_router(session_router)
