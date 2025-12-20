from fastapi import Depends, Path

from app.core.exceptions import AdminAccessRequiredException, AccessDeniedException
from app.core.security.dependencies import get_current_user
from app.db.models.enums import UserRole


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != UserRole.ADMIN:
        raise AdminAccessRequiredException()
    return current_user


def require_owner_or_admin(user_id: int = Path(...), current_user: dict = Depends(get_current_user)):
    if current_user["user_id"] == user_id:
        return current_user
    if current_user.get("role") == UserRole.ADMIN:
        return current_user
    raise AccessDeniedException()
