from redis.asyncio import Redis


async def is_token_blacklisted(redis: Redis, jti: str) -> bool:
    key = f"blacklist:token:{jti}"
    return await redis.exists(key)


async def blacklist_token(redis: Redis, jti: str, expire_seconds: int):
    key = f"blacklist:token:{jti}"
    await redis.setex(key, expire_seconds, "revoked")
