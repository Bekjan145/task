from redis.asyncio import Redis, ConnectionPool
from app.core.settings import settings

pool: ConnectionPool | None = None


async def init_redis():
    global pool
    pool = ConnectionPool.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=50,
    )


async def get_redis() -> Redis:
    if pool is None:
        await init_redis()
    return Redis(connection_pool=pool)


async def close_redis():
    global pool
    if pool:
        await pool.disconnect()
        pool = None
