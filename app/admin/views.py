from sqladmin import ModelView

from app.core import hash_password
from app.core.validators import process_phone
from app.db.models.user import User


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    column_list = [User.id, User.phone, User.username, User.role, User.created_at]
    column_searchable_list = [User.id, User.username]
    column_sortable_list = [User.id, User.created_at, User.role]
    column_default_sort = [(User.created_at, True)]

    form_excluded_columns = [User.created_at]
    column_details_exclude_list = [User.hashed_password]

    page_size = 50

    async def on_model_change(self, data: dict, model: User, is_created: bool, request) -> None:
        phone = data.get("phone")
        if phone:
            data["phone"] = process_phone(phone)

        password = data.get("hashed_password")
        if password and (is_created or password != "***"):
            data["hashed_password"] = hash_password(password)

        if is_created and not data.get("hashed_password"):
            raise ValueError("Password is required")
