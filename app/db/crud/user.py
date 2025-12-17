from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.models.user import User
from app.db.database import get_db


class UserCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_phone(self, phone: str) -> Optional[User]:
        return self.db.query(User).filter(User.phone == phone).first()

    def create(self, phone: str, hashed_password: str) -> User:

        user = User(phone=phone, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        user = self.get_by_id(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    def exists_by_phone(self, phone: str) -> bool:
        return self.db.query(User).filter(User.phone == phone).count() > 0

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.db.query(User).offset(skip).limit(limit).all()


def get_user_crud(db: Session = Depends(get_db)) -> UserCRUD:
    return UserCRUD(db)
