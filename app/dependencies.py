from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.mail import MailService, get_mail_service
from app.services.security import SecurityService, get_security_service
from app.services.user import UserService


async def get_user_service(
    db: AsyncSession = Depends(get_db),
    security: SecurityService = Depends(get_security_service),
    mail: MailService = Depends(get_mail_service)
) -> UserService:
    security = SecurityService()

    return UserService(
        db=db,
        security=security,
        mail=mail
    )
