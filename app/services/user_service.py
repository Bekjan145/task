from typing import List

from fastapi import Depends

from app.core.exceptions import UserNotFoundException, PhoneAlreadyExistsException
from app.core.security.dependencies import get_current_user
from app.core.security.hashing import hash_password
from app.core.validators import process_phone
from app.db.crud.user import UserCRUD
from app.db.models.user import User
from app.schemas.user import UserCreateAdmin, UserPut, UserPatch


class UserService:
    def __init__(self, user_crud: UserCRUD = Depends(), current_user: dict = Depends(get_current_user)):
        self.user_crud = user_crud
        self.current_user = current_user

    async def list_users(self, skip: int, limit: int) -> List[User]:
        return await self.user_crud.list_users(skip=skip, limit=limit)

    async def get_user(self, user_id: int) -> User:
        user = await self.user_crud.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return user

    async def create_user(self, user_data: UserCreateAdmin) -> User:
        normalized_phone = process_phone(user_data.phone)

        exists = await self.user_crud.exists_by_phone(normalized_phone)
        if exists:
            raise PhoneAlreadyExistsException()

        hashed_pwd = hash_password(user_data.password)

        return await self.user_crud.create(
            phone=normalized_phone,
            hashed_password=hashed_pwd,
            username=user_data.username,
            role=user_data.role
        )

    async def put_user(self, user_id: int, user_data: UserPut) -> User | None:
        user = await self.user_crud.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        update_data = {}

        if user_data.username is not None:
            update_data["username"] = user_data.username or None

        if user_data.phone is not None:
            normalized_phone = process_phone(user_data.phone)

            if normalized_phone != user.phone:
                exists = await self.user_crud.exists_by_phone(normalized_phone)
                if exists:
                    raise PhoneAlreadyExistsException()
            update_data["phone"] = normalized_phone

        if not update_data:
            return user

        return await self.user_crud.update(user_id, **update_data)

    async def patch_user(self, user_id: int, user_data: UserPatch) -> User | None:
        user = await self.user_crud.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        update_data = {}
        if "username" in user_data.model_fields_set:
            update_data["username"] = user_data.username or None

        if "phone" in user_data.model_fields_set and user_data.phone is not None:
            normalized_phone = process_phone(user_data.phone)

            if normalized_phone != user.phone:
                exists = await self.user_crud.exists_by_phone(normalized_phone)
                if exists:
                    raise PhoneAlreadyExistsException()

            update_data["phone"] = normalized_phone

        if not update_data:
            return user

        return await self.user_crud.update(user_id, **update_data)

    async def delete_user(self, user_id: int):
        user = await self.user_crud.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        await self.user_crud.delete(user_id)
