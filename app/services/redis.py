import aioredis

from app.config import config

_redis = None


async def get_redis():
    global _redis
    if not _redis:
        _redis = await aioredis.from_url(
            f"redis://{config.redis.host}:{config.redis.port}/{config.redis.db}",
            encoding='utf8',
            decode_responses=True
        )

    return _redis
