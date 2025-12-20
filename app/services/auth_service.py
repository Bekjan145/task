import uuid

from fastapi import Depends
from redis.asyncio import Redis

from app.core import verify_token_payload, get_redis, settings, PhoneAlreadyExistsException, \
    InvalidCredentialsException, TokenInvalidException, UserNotFoundException, InvalidTokenTypeException
from app.core.security import blacklist_token
from app.core.security.hashing import hash_password, verify_password
from app.core.security.jwt import create_access_token, create_refresh_token
from app.core.validators import normalize_phone, validate_phone
from app.db.crud.user import UserCRUD


class AuthService:
    def __init__(self, user_crud: UserCRUD = Depends(), redis: Redis = Depends(get_redis)):
        self.user_crud = user_crud
        self.redis = redis

    def register(self, phone: str, password: str) -> tuple[str, str]:
        validate_phone(phone)
        normalized_phone = normalize_phone(phone)

        if self.user_crud.exists_by_phone(normalized_phone):
            raise PhoneAlreadyExistsException()

        hashed_pwd = hash_password(password)
        user = self.user_crud.create(normalized_phone, hashed_pwd)

        # Generate tokens
        return self._generate_tokens(user.id, user.phone, user.role)

    def login(self, phone: str, password: str) -> tuple[str, str]:
        validate_phone(phone)
        normalized_phone = normalize_phone(phone)

        user = self.user_crud.get_by_phone(normalized_phone)
        if not user or not user.hashed_password:
            raise InvalidCredentialsException()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        return self._generate_tokens(user.id, user.phone, user.role)

    async def refresh_token(self, refresh_token: str) -> str:
        payload = await verify_token_payload(refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        phone = payload.get("phone")
        role = payload.get("role")

        if user_id is None:
            raise TokenInvalidException()

        user = self.user_crud.get_by_id(int(user_id))
        if not user:
            raise UserNotFoundException()

        return self._generate_access_token(user_id, phone, role)

    async def logout(self, jti: str) -> None:
        if not jti:
            raise InvalidTokenTypeException()
        await blacklist_token(redis=self.redis, jti=jti, expire_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    def _generate_tokens(self, user_id: int, phone: str, role: str) -> tuple[str, str]:
        token_jti = str(uuid.uuid4())
        access_token = create_access_token(data={"sub": str(user_id), "phone": phone, "jti": token_jti, "role": role})
        refresh_token = create_refresh_token(data={"sub": str(user_id), "phone": phone, "role": role})

        return access_token, refresh_token

    def _generate_access_token(self, user_id: str, phone: str, role: str) -> str:
        token_jti = str(uuid.uuid4())
        return create_access_token(data={"sub": user_id, "phone": phone, "jti": token_jti, "role": role})
