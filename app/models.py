from sqlalchemy import Column, Integer, String

from app.database import Base


class OTPRecord(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True, nullable=False)
    code = Column(String(4), nullable=False)
