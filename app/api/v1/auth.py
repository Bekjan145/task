from fastapi import APIRouter
from fastapi.params import Depends

from app.core.security import get_current_user
from app.schemas import TokenResponse, UserCreate, UserLogin, TokenRefreshRequest, \
    TokenRefreshResponse, LogoutResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, auth_service: AuthService = Depends()):
    access_token, refresh_token = auth_service.register(phone=user_data.phone, password=user_data.password)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, auth_service: AuthService = Depends()):
    access_token, refresh_token = auth_service.login(phone=user_data.phone, password=user_data.password)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh-token", response_model=TokenRefreshResponse)
async def refresh_access_token(request: TokenRefreshRequest, auth_service: AuthService = Depends()):
    access_token = await auth_service.refresh_token(request.refresh_token)
    return TokenRefreshResponse(access_token=access_token)


@router.post("/logout", response_model=LogoutResponse)
async def logout(current_user: dict = Depends(get_current_user), auth_service: AuthService = Depends()):
    token_jti = current_user.get('token_jti')
    await auth_service.logout(token_jti)
    return LogoutResponse()
