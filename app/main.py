import random

from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import OTPRecord
from app.schemas import SendOTPRequest, VerifyOTPRequest
from app.settings import settings

app = FastAPI()

Base.metadata.create_all(bind=engine)


def new_otp() -> str:
    return f"{random.randint(settings.OTP_MIN_VALUE, settings.OTP_MAX_VALUE):0{settings.OTP_LENGTH}d}"


@app.post("/send-otp")
async def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    code = new_otp()

    existing = db.query(OTPRecord).filter(OTPRecord.phone == request.phone).first()

    if existing:
        existing.code = code
    else:
        otp_record = OTPRecord(phone=request.phone, code=code)
        db.add(otp_record)

    db.commit()

    return {
        "phone": request.phone,
        "otp_code": code
    }


@app.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    existing = db.query(OTPRecord).filter(OTPRecord.phone == request.phone).first()

    if not existing:
        raise HTTPException(status_code=400, detail="OTP not found")

    if existing.code != request.code:
        raise HTTPException(status_code=400, detail="Incorrect code")

    db.delete(existing)
    db.commit()

    return {
        "verified": True,
        "phone": request.phone
    }
