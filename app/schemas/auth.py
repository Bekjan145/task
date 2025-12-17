from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    phone: str = Field(..., min_length=9, max_length=20, description="Phone number")
    password: str = Field(..., min_length=8, description="Password")


class UserLogin(BaseModel):
    phone: str = Field(..., min_length=9, max_length=20)
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    message: str = "Successfully logged out"
