from fastapi import APIRouter, Depends

from app.schemas.otp import SendOTPRequest, SendOTPResponse, VerifyOTPRequest, VerifyOTPResponse
from app.services.otp_service import OTPService

router = APIRouter(prefix="/otp", tags=["otp"])


@router.post("/send-otp", response_model=SendOTPResponse)
async def send_otp(request: SendOTPRequest, otp_service: OTPService = Depends()):
    result = await otp_service.send_otp(request.phone)
    return SendOTPResponse(**result)


@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(request: VerifyOTPRequest, otp_service: OTPService = Depends()):
    result = await otp_service.verify_otp(request.phone, request.code)
    return VerifyOTPResponse(**result)
