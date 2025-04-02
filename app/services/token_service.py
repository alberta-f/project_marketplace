from uuid import UUID

from app.core.config_file import config
from app.repo.repo_redis import RedisRepository
from app.repo.token import TokenRepository


class TokenService:
    def __init__(self, redis_repo: RedisRepository):
        self.repos: dict[str, TokenRepository] = {
            'activation': TokenRepository(
                redis_repo=redis_repo,
                token_type='activation',
                ttl=config.jwt.single_use_expire_mins * 60,
                single_use=True
            ),

            'access': TokenRepository(
                redis_repo=redis_repo,
                token_type='access',
                ttl=None,
                single_use=False
            ),

            'reset': TokenRepository(
                redis_repo=redis_repo,
                token_type='reset',
                ttl=config.jwt.single_use_expire_mins * 60,
                single_use=True
            )
        }

    async def generate(self, token_type: str, user_id: UUID) -> str:
        return await self.repos[token_type].generate_token(user_id)

    async def validate(self, token_type: str, token: str) -> UUID | None:
        return await self.repos[token_type].validate_token(token)

    async def delete(self, token_type: str, token: str, user_id: UUID):
        await self.repos[token_type].delete_token(token, user_id)

    async def delete_all(self, token_type: str, user_id: UUID):
        await self.repos[token_type].delete_all_user_tokens(user_id)
