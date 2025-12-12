from redis.asyncio import Redis, ConnectionPool
from app.core.settings import settings

pool = None


async def init_redis():
    global pool
    pool = ConnectionPool.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=50
    )


async def get_redis():
    return Redis(connection_pool=pool)


async def close_redis():
    if pool:
        await pool.disconnect()
