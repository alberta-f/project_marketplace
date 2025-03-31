from datetime import datetime, timedelta, timezone
from typing import Union
from uuid import UUID

from jose import JWTError, jwt

from app.config import config
from app.services.redis import get_redis


async def store_token(user_id: UUID,
                      token: str,
                      token_type: str,
                      expires_in: int = config.jwt.access_expire_mins * 60):

    redis = await get_redis()
    redis_key = f"{token_type}:{token}"
    await redis.set(redis_key, str(user_id), ex=expires_in)


# token_types: access, email, password
async def create_token(user_id: UUID,
                       token_type: str,
                       expires_in: int = config.jwt.access_expire_mins * 60) -> str:

    expire = datetime.now(timezone.utc) + timedelta(minutes=config.jwt.access_expire_mins)
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "exp": expire
    }

    token = jwt.encode(payload,
                      config.jwt.secret_key,
                      algorithm=config.jwt.algorithm)

    await store_token(user_id=user_id,
                      token=token,
                      token_type=token_type,
                      expires_in=expires_in)

    return token


async def decode_token(token: str) -> Union[dict, None]:
    try:
        payload = jwt.decode(token,
                             config.jwt.secret_key,
                             algorithms=config.jwt.algorithm)

        return payload

    except (JWTError, ValueError):
        return None


async def delete_token(redis_key: str = None):
    redis = await get_redis()

    await redis.delete(redis_key)


async def verify_token(token: str, exc_token_type: str) -> UUID | None:
    payload = await decode_token(token)

    if not payload or payload.get("type") != exc_token_type:
        return None

    user_id = payload.get("sub")
    redis = await get_redis()
    redis_key = f"{exc_token_type}:{token}"
    stored_token = await redis.get(str(redis_key))

    if stored_token is None:
        return None

    if exc_token_type != 'access':
        await delete_token(redis_key)

    return UUID(user_id)
