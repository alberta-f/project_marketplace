from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.category import CategoryService
from app.services.mail import MailService
from app.services.security import SecurityService
from app.services.token import TokenService
from app.services.user import UserService


def get_token_service():
    return TokenService()


def get_mail_service():
    return MailService()


def get_security_service():
    return SecurityService()

def get_user_service(
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

def get_category_service(
        db: AsyncSession = Depends(get_db),
):
    return CategoryService(db)
