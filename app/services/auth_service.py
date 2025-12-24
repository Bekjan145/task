import uuid

from fastapi import Depends
from redis.asyncio import Redis

from app.core import verify_token_payload, get_redis, settings, PhoneAlreadyExistsException, \
    InvalidCredentialsException, TokenInvalidException, UserNotFoundException, InvalidTokenTypeException
from app.core.security import blacklist_token
from app.core.security.hashing import hash_password, verify_password
from app.core.security.jwt import create_access_token, create_refresh_token
from app.core.validators import process_phone
from app.db.crud.user import UserCRUD


class AuthService:
    def __init__(self, user_crud: UserCRUD = Depends(), redis: Redis = Depends(get_redis)):
        self.user_crud = user_crud
        self.redis = redis

    async def register(self, phone: str, password: str) -> tuple[str, str]:
        normalized_phone = process_phone(phone)

        exists = await self.user_crud.exists_by_phone(normalized_phone)
        if exists:
            raise PhoneAlreadyExistsException()

        hashed_pwd = hash_password(password)
        user = await self.user_crud.create(normalized_phone, hashed_pwd)

        return self._generate_tokens(user.id, user.phone, user.role)

    async def login(self, phone: str, password: str) -> tuple[str, str]:
        normalized_phone = process_phone(phone)

        user = await self.user_crud.get_by_phone(normalized_phone)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        return self._generate_tokens(user.id, user.phone, user.role)

    async def refresh_token(self, refresh_token: str) -> str:
        payload = verify_token_payload(refresh_token, token_type="refresh")

        user_id = payload.get("sub")
        if not user_id:
            raise TokenInvalidException()

        user = await self.user_crud.get_by_id(int(user_id))
        if not user:
            raise UserNotFoundException()

        return self._generate_access_token(user_id, user.phone, user.role)

    async def logout(self, jti: str) -> None:
        if not jti:
            raise InvalidTokenTypeException()

        expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        await blacklist_token(redis=self.redis, jti=jti, expire_seconds=expire_seconds)

    def _generate_tokens(self, user_id: int, phone: str, role: str) -> tuple[str, str]:
        token_jti = str(uuid.uuid4())
        access_token = create_access_token(data={"sub": str(user_id), "phone": phone, "jti": token_jti, "role": role})
        refresh_token = create_refresh_token(data={"sub": str(user_id), "phone": phone, "role": role})

        return access_token, refresh_token

    def _generate_access_token(self, user_id: str, phone: str, role: str) -> str:
        token_jti = str(uuid.uuid4())
        return create_access_token(data={"sub": user_id, "phone": phone, "jti": token_jti, "role": role})
