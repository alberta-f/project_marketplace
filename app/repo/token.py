from datetime import datetime, timedelta, timezone
from typing import Union
from uuid import UUID

from jose import JWTError, jwt

from app.core.config_file import config
from app.repo.repo_redis import RedisRepository


class TokenRepository:
    def __init__(
        self,
        redis_repo: RedisRepository,
        token_type: str,
        ttl: int | None,
        single_use: bool = True
    ):
        self.redis = redis_repo
        self.token_type = token_type
        self.ttl = ttl
        self.single_use = single_use
        self.secret_key = config.jwt.secret_key
        self.algorithm = config.jwt.algorithm

    def _make_key(self, token: str, user_id: UUID) -> str:
        return f"{self.token_type}:{user_id}:{token}"

    def _generate_token(self, user_id: UUID) -> str:
        expire = datetime.now(timezone.utc) + timedelta(seconds=self.ttl)
        payload = {
            "sub": str(user_id),
            "type": self.token_type,
            "exp": expire
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    async def generate_token(self, user_id: UUID) -> str:
        token = self._generate_token(user_id)
        key = self._make_key(token, user_id)
        await self.redis.set(key, str(user_id), ttl=self.ttl)
        return token

    async def decode_token(self, token: str) -> Union[dict, None]:
        try:
            return jwt.decode(token,
                              self.secret_key,
                              algorithms=[self.algorithm])

        except (JWTError, ValueError):
            return None

    async def validate_token(self, token: str) -> UUID | None:
        payload = await self.decode_token(token)

        if not payload or payload.get("type") != self.token_type:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        redis_key = self._make_key(token, user_id)
        stored_token = await self.redis.get(redis_key)
        if not stored_token:
            return None

        if self.single_use:
            await self.redis.delete(redis_key)

        return UUID(user_id)

    async def delete_token(self, token: str, user_id: UUID):
        key = self._make_key(token, user_id)
        await self.redis.delete(key)

    async def delete_all_user_tokens(self, user_id: UUID):
        pattern = f"{self.token_type}:{user_id}:*"
        keys = await self.redis.redis.keys(pattern)  # доступ к raw Redis
        if keys:
            await self.redis.redis.delete(*keys)
