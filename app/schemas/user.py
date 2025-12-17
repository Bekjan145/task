from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class UserResponse(BaseModel):
    id: int
    phone: str
    username: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
