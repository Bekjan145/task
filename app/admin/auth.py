from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.security.hashing import verify_password
from app.core.validators import process_phone
from app.db.crud.user import UserCRUD
from app.db.database import get_db
from app.db.models.enums import UserRole


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool | None:
        form = await request.form()
        phone = form.get("username")
        password = form.get("password")

        if not phone or not password:
            return False

        async for db in get_db():
            user_crud = UserCRUD(db=db)

            normalized_phone = process_phone(phone)

            user = await user_crud.get_by_phone(normalized_phone)
            if not user or user.role != UserRole.ADMIN:
                return False

            if not verify_password(password, user.hashed_password):
                return False

            request.session["user_id"] = user.id
            request.session["role"] = user.role
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> RedirectResponse | bool:
        user_id = request.session.get("user_id")
        role = request.session.get("role")

        if not user_id or role != UserRole.ADMIN:
            return RedirectResponse(url=request.url_for("admin:login"), status_code=302)

        return True
