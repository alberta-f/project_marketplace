from redis.asyncio import Redis

from app.core.config_file import config

redis_ = Redis.from_url(url=config.redis.url,
                       encoding='utf8',
                       decode_responses=True)


async def get_redis():
    yield redis_
