from datetime import datetime, timedelta, timezone
from typing import Union
from uuid import UUID

from jose import JWTError, jwt

from app.config import config


def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=config.jwt.access_expire_mins)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(payload,
                      config.jwt.secret_key,
                      algorithm=config.jwt.algorithm)


def verify_access_token(token: str) -> Union[UUID, None]:
    try:
        payload = jwt.decode(token,
                             config.jwt.secret_key,
                             algorithms=config.jwt.algorithm)

        return UUID(payload.get('sub'))

    except (JWTError, ValueError):
        return None
