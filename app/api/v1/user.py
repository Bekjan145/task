from typing import List

from fastapi import status, APIRouter
from fastapi.params import Depends

from app.core.permissions import require_admin, require_owner_or_admin
from app.schemas import UserResponse
from app.schemas.user import UserCreateAdmin, UserPut, UserPatch
from app.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user_service: UserService = Depends()):
    current_user_id = user_service.current_user["user_id"]
    return await user_service.get_user(current_user_id)


@router.get("/users", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, _: dict = Depends(require_admin),
                     user_service: UserService = Depends()):
    return await user_service.list_users(skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, _: dict = Depends(require_owner_or_admin), user_service: UserService = Depends()):
    return await user_service.get_user(user_id)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateAdmin, _: dict = Depends(require_admin),
                      user_service: UserService = Depends()):
    return await user_service.create_user(user_data)


@router.put("/users/{user_id}", response_model=UserResponse)
async def put_user(user_id: int, user_data: UserPut, _: dict = Depends(require_owner_or_admin),
                      user_service: UserService = Depends()):
    return await user_service.put_user(user_id, user_data)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def patch_user(user_id: int, user_data: UserPatch, _: dict = Depends(require_owner_or_admin),
                     user_service: UserService = Depends()):
    return await user_service.patch_user(user_id, user_data)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, _: dict = Depends(require_admin), user_service: UserService = Depends()):
    await user_service.delete_user(user_id)
