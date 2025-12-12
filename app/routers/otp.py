import random

from fastapi import HTTPException, status, APIRouter
from fastapi.params import Depends
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.redis_client import get_redis
from app.schemas import SendOTPRequest, VerifyOTPRequest
from app.core.settings import settings

router = APIRouter(prefix="/otp", tags=["otp"])


def new_otp() -> str:
    return f"{random.randint(settings.OTP_MIN_VALUE, settings.OTP_MAX_VALUE):0{settings.OTP_LENGTH}d}"


@router.post("/send-otp")
async def send_otp(request: SendOTPRequest, redis: Redis = Depends(get_redis)):
    code = new_otp()

    otp_key = f"otp:{request.email}"

    await redis.setex(
        otp_key,
        int(settings.OTP_EXPIRE_MINUTES * 60),
        code
    )

    return {
        "email": request.email,
        "otp_code": code
    }


@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest, redis: Redis = Depends(get_redis)):
    try:
        otp_key = f"otp:{request.email}"
        stored_code = await redis.get(otp_key)

        if not stored_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired or not found")

        stored_otp = stored_code.decode("utf-8")

        if stored_otp != request.code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect code")

        await redis.delete(otp_key)

        return {
            "verified": True,
            "email": request.email
        }
    except RedisError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Service temporarily unavailable")
