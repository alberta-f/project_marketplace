from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.security import SecurityService
from app.services.user import UserService


async def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    security = SecurityService()

    return UserService(
        db=db,
        security_service=security,
    )

def get_security_service():
    return SecurityService()
