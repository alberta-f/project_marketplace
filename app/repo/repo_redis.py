from redis.asyncio import Redis


class RedisRepository:
    def __init__(self, redis: Redis):
        self.redis = redis


    async def set(self, key: str, value: str, ttl: int):
        await self.redis.set(key, value, ttl)


    async def get(self, key: str):
        await self.redis.get(key)


    async def delete(self, key: str):
        await self.redis.delete(key)
