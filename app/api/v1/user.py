from fastapi import HTTPException, status, APIRouter
from fastapi.params import Depends

from app.core.security import get_current_user
from app.db.crud.user import UserCRUD, get_user_crud
from app.schemas import UserResponse

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user),
                                user_crud: UserCRUD = Depends(get_user_crud)):
    user = user_crud.get_by_id(current_user["user_id"])

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user
