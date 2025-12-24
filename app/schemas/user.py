from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from app.db.models.enums import UserRole


class UserResponse(BaseModel):
    id: int
    phone: str
    username: Optional[str] = None
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreateAdmin(BaseModel):
    phone: str = Field(..., min_length=9, max_length=20, description="Phone number")
    password: str = Field(..., min_length=8, description="Password")
    username: Optional[str] = None
    role: UserRole = UserRole.USER


class UserPut(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None

    model_config = {"extra": "forbid"}


class UserPatch(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None

    model_config = {"extra": "forbid", "populate_by_name": True, }
