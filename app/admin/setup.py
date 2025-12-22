from sqladmin import Admin
from app.db.database import engine
from app.admin.auth import AdminAuth
from app.admin.views import UserAdmin
from app.core.settings import settings


def setup_admin(app):
    admin = Admin(app, engine, authentication_backend=AdminAuth(secret_key=settings.SECRET_KEY))
    admin.add_view(UserAdmin)
    return admin
