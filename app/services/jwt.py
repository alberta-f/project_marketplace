from datetime import datetime, timedelta, timezone
from typing import Union
from uuid import UUID

from jose import JWTError, jwt

from app.config import config
from app.services.redis import get_redis


async def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=config.jwt.access_expire_mins)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(payload,
                      config.jwt.secret_key,
                      algorithm=config.jwt.algorithm)


async def store_token(user_id: UUID,
                      token: str,
                      expires_in: int = config.jwt.access_expire_mins * 60):

    redis = await get_redis()
    await redis.set(str(user_id), token, ex=expires_in)


async def decode_token(token: str) -> Union[UUID, None]:
    try:
        payload = jwt.decode(token,
                             config.jwt.secret_key,
                             algorithms=config.jwt.algorithm)

        return UUID(payload.get('sub'))

    except (JWTError, ValueError):
        return None


async def verify_access_token(token: str) -> UUID | None:
    user_id = await decode_token(token)

    if not user_id:
        return None

    redis = await get_redis()
    stored_token = await redis.get(str(user_id))

    if stored_token != token:
        return None

    return user_id


async def delete_token(user_id:UUID):
    redis = await get_redis()

    await redis.delete(str(user_id))
