from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from redis.asyncio import Redis

from app.core.security.blacklist import is_token_blacklisted
from app.core.settings import settings
from app.core.redis_client import get_redis

security = HTTPBearer()


async def verify_token_payload(token: str, token_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != token_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                           redis: Redis = Depends(get_redis)) -> dict:
    token = credentials.credentials
    payload = await verify_token_payload(token, token_type="access")

    jti = payload.get("jti")
    if jti and await is_token_blacklisted(redis, jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    return {"user_id": int(user_id), "phone": payload.get("phone"), "token_jti": jti}
