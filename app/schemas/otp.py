from pydantic import BaseModel, Field


class SendOTPRequest(BaseModel):
    phone: str = Field(..., min_length=9, max_length=20, description="Phone number")


class SendOTPResponse(BaseModel):
    phone: str
    otp_code: str
    remaining_attempts: int
    next_request_in: int


class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., min_length=9, max_length=20)
    code: str = Field(..., min_length=4, max_length=4, description="OTP code")


class VerifyOTPResponse(BaseModel):
    verified: bool
    phone: str
