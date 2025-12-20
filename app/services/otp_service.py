import random
from typing import Tuple

from fastapi import Depends
from redis.asyncio import Redis

from app.core import OTPRateLimitException, OTPCooldownException, OTPVerifyAttemptsExceededException, \
    OTPIncorrectException, OTPExpiredOrNotFoundException
from app.core.redis_client import get_redis
from app.core.settings import settings
from app.core.validators import validate_phone, normalize_phone


class OTPService:
    def __init__(self, redis: Redis = Depends(get_redis)):
        self.redis = redis

    def _generate_otp(self) -> str:
        return f"{random.randint(settings.OTP_MIN_VALUE, settings.OTP_MAX_VALUE):0{settings.OTP_LENGTH}d}"

    async def _check_cooldown(self, phone: str) -> Tuple[bool, int]:
        key = f"otp:cooldown:{phone}"
        remaining = await self.redis.ttl(key)
        if remaining > 0:
            return False, remaining
        return True, 0

    async def _check_rate_limit(self, phone: str) -> Tuple[bool, int]:
        key = f"otp:rate_limit:{phone}"
        attempts = await self.redis.get(key)
        current = int(attempts) if attempts else 0

        if current >= settings.OTP_MAX_ATTEMPTS:
            return False, 0

        attempts_left = settings.OTP_MAX_ATTEMPTS - current - 1

        return True, attempts_left

    async def _set_cooldown(self, phone: str):
        key = f"otp:cooldown:{phone}"
        await self.redis.setex(key, settings.OTP_COOLDOWN_SECONDS, "active")

    async def _increment_rate_limit(self, phone: str):
        key = f"otp:rate_limit:{phone}"
        attempts = await self.redis.incr(key)

        if attempts == 1:
            await self.redis.expire(key, settings.OTP_MAX_ATTEMPTS_WINDOW)

    async def _check_verify_attempts(self, phone: str) -> Tuple[bool, int]:
        key = f"otp:verify_attempts:{phone}"
        attempts = await self.redis.get(key)
        current_attempts = int(attempts) if attempts else 0

        if current_attempts >= settings.OTP_MAX_VERIFY_ATTEMPTS:
            return False, 0

        attempts_left = settings.OTP_MAX_VERIFY_ATTEMPTS - current_attempts
        return True, attempts_left

    async def _increment_verify_attempts(self, phone: str):
        key = f"otp:verify_attempts:{phone}"
        attempts = await self.redis.incr(key)

        if attempts == 1:
            await self.redis.expire(key, settings.OTP_VERIFY_ATTEMPTS_WINDOW)

    async def _reset_verify_attempts(self, phone: str):
        key = f"otp:verify_attempts:{phone}"
        await self.redis.delete(key)

    async def send_otp(self, phone: str) -> dict:
        validate_phone(phone)
        normalized_phone = normalize_phone(phone)

        is_available, remaining = await self._check_cooldown(normalized_phone)
        if not is_available:
            raise OTPCooldownException(remaining)

        is_allowed, attempts_left = await self._check_rate_limit(normalized_phone)
        if not is_allowed:
            raise OTPRateLimitException()

        code = self._generate_otp()
        otp_key = f"otp:{normalized_phone}"
        await self.redis.setex(otp_key, int(settings.OTP_EXPIRE_MINUTES * 60), code)

        await self._set_cooldown(normalized_phone)
        await self._increment_rate_limit(normalized_phone)

        return {
            "phone": normalized_phone,
            "otp_code": code,
            "remaining_attempts": attempts_left,
            "next_request_in": settings.OTP_COOLDOWN_SECONDS
        }

    async def verify_otp(self, phone: str, code: str) -> dict:
        validate_phone(phone)
        normalized_phone = normalize_phone(phone)

        is_allowed, _ = await self._check_verify_attempts(normalized_phone)
        if not is_allowed:
            raise OTPVerifyAttemptsExceededException()

        otp_key = f"otp:{normalized_phone}"
        stored = await self.redis.get(otp_key)
        if not stored:
            raise OTPExpiredOrNotFoundException()

        stored_code = stored.decode("utf-8") if isinstance(stored, bytes) else stored

        if stored_code != code:
            await self._increment_verify_attempts(normalized_phone)
            raise OTPIncorrectException()

        await self.redis.delete(otp_key)
        await self._reset_verify_attempts(normalized_phone)

        return {"verified": True, "phone": normalized_phone}
