from fastapi import Depends

from app.core.exceptions import UserNotFoundException, PhoneAlreadyExistsException
from app.core.security.dependencies import get_current_user
from app.core.security.hashing import hash_password
from app.core.validators import validate_phone, normalize_phone
from app.db.crud.user import UserCRUD
from app.db.models.user import User
from app.schemas.user import UserCreateAdmin, UserUpdate, UserPatch


class UserService:
    def __init__(self, user_crud: UserCRUD = Depends(), current_user: dict = Depends(get_current_user)):
        self.user_crud = user_crud
        self.current_user = current_user

    def list_users(self, skip: int, limit: int) -> list[User]:
        return self.user_crud.list_users(skip=skip, limit=limit)

    def get_user(self, user_id: int) -> User:
        user = self.user_crud.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return user

    def create_user(self, user_data: UserCreateAdmin) -> User:
        validate_phone(user_data.phone)
        normalized_phone = normalize_phone(user_data.phone)

        if self.user_crud.exists_by_phone(normalized_phone):
            raise PhoneAlreadyExistsException()

        hashed_pwd = hash_password(user_data.password)

        user = self.user_crud.create(
            phone=normalized_phone,
            hashed_password=hashed_pwd,
            username=user_data.username,
            role=user_data.role
        )

        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> User | None:
        user = self.user_crud.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        update_dict = {}
        if user_data.username is not None:
            update_dict["username"] = user_data.username
        if user_data.phone is not None:
            validate_phone(user_data.phone)
            normalized_phone = normalize_phone(user_data.phone)
            update_dict["phone"] = normalized_phone

        updated = self.user_crud.update(user_id, **update_dict)
        return updated

    def patch_user(self, user_id: int, user_data: UserPatch) -> User | None:
        user = self.user_crud.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        update_dict = {}
        if user_data.username is not None:
            update_dict["username"] = user_data.username
        if user_data.phone is not None:
            validate_phone(user_data.phone)
            normalized_phone = normalize_phone(user_data.phone)
            update_dict["phone"] = normalized_phone

        updated = self.user_crud.update(user_id, **update_dict)
        return updated

    def delete_user(self, user_id: int):
        if self.user_crud.get_by_id(user_id) is None:
            raise UserNotFoundException()

        self.user_crud.delete(user_id)
