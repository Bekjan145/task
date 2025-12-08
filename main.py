from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random

app = FastAPI()

otp = {}


class SendOTPRequest(BaseModel):
    user_id: str


class VerifyOTPRequest(BaseModel):
    user_id: str
    code: str


def new_otp() -> str:
    return f"{random.randint(1000, 9999)}"


@app.post("/send-otp")
async def send_otp(request: SendOTPRequest):
    user_id = request.user_id
    code = new_otp()

    otp[user_id] = code

    return {
        "message": "OTP muvaffaqiyatli yaratildi",
        "user_id": user_id,
        "otp_code": code,
    }


@app.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    user_id = request.user_id
    entered_code = request.code

    if user_id not in otp:
        raise HTTPException(status_code=400, detail="OTP topilmadi yoki muddati o'tgan")

    if otp[user_id] == entered_code:
        del otp[user_id]
        return {
            "message": "OTP muvaffaqiyatli tasdiqlandi!",
            "verified": True,
            "user_id": user_id
        }
    else:
        raise HTTPException(status_code=400, detail="Noto'g'ri OTP kodi")
