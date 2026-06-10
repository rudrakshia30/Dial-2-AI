import os
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL")

redis_client = None


async def init_redis():
    global redis_client
    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True
    )


async def get(key):
    return await redis_client.get(key)


async def set(key, value, ex=None):
    return await redis_client.set(key, value, ex=ex)


async def delete(key):
    return await redis_client.delete(key)