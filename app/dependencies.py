from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.repo.repo_redis import RedisRepository
from app.services.mail_service import MailService
from app.services.security_service import SecurityService
from app.services.token_service import TokenService
from app.services.user_service import UserService


async def get_user_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> UserService:
    redis_repo = RedisRepository(redis)
    token_service = TokenService(redis_repo)
    security = SecurityService()
    mail_service = MailService()

    return UserService(
        db=db,
        token_service=token_service,
        security_service=security,
        mail_service=mail_service,
    )
