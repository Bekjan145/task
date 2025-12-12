import uuid

from fastapi import HTTPException, status, APIRouter
from fastapi.params import Depends
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User
from app.redis_client import get_redis
from app.schemas import TokenResponse, UserCreate, UserLogin, TokenRefreshRequest, \
    TokenRefreshResponse
from app.core.security import hash_password, create_access_token, create_refresh_token, verify_password, verify_token, \
    get_current_user
from app.core.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_pwd = hash_password(user_data.password)

    username = user_data.email.split("@")[0]

    new_user = User(
        email=user_data.email,
        username=username,
        hashed_password=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token_jti = str(uuid.uuid4())

    access_token_data = {"sub": str(new_user.id), "email": new_user.email, "jti": token_jti}
    access_token = create_access_token(data=access_token_data)
    refresh_token = create_refresh_token(data={"sub": str(new_user.id), "email": new_user.email})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token_jti = str(uuid.uuid4())

    access_token_data = {"sub": str(user.id), "email": user.email, "jti": token_jti}
    access_token = create_access_token(data=access_token_data)
    refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh-token", response_model=TokenRefreshResponse)
async def refresh_access_token(request: TokenRefreshRequest):
    payload = verify_token(request.refresh_token, token_type="refresh")
    user_id = payload.get("sub")
    email = payload.get("email")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    token_jti = str(uuid.uuid4())

    access_token_data = {"sub": user_id, "email": email, "jti": token_jti}
    access_token = create_access_token(data=access_token_data)

    return TokenRefreshResponse(access_token=access_token)


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user), redis: Redis = Depends(get_redis)):
    try:
        token_jti = current_user.get('token_jti')
        blacklist_key = f"blacklist:token:{token_jti}"

        await redis.setex(
            blacklist_key,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "revoked"
        )

        return {"message": "Successfully logged out"}
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
