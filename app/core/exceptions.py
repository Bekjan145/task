from typing import Any

from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    detail: str = "An error occurred"

    def __init__(self, **kwargs: Any):
        detail = kwargs.pop("detail", self.detail)
        super().__init__(status_code=self.status_code, detail=detail, **kwargs)


class AuthException(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Authentication error"


class InvalidCredentialsException(AuthException):
    detail = "Invalid phone or password"


class TokenInvalidException(AuthException):
    detail = "Could not validate credentials"


class TokenRevokedException(AuthException):
    detail = "Token revoked"


class InvalidTokenTypeException(AuthException):
    detail = "Invalid token type"


class UserNotFoundException(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found"


class PhoneAlreadyExistsException(BaseHTTPException):
    detail = "Phone already registered"


class InvalidPhoneFormatException(BaseHTTPException):
    detail = "Invalid phone number format. Expected format: +998901234567 or 901234567"


class AccessDeniedException(BaseHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Access denied"


class AdminAccessRequiredException(AccessDeniedException):
    detail = "Admin access required"


class OTPException(BaseHTTPException):
    detail = "OTP error"


class OTPCooldownException(BaseHTTPException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS

    def __init__(self, remaining_seconds: int):
        detail = f"Please wait {remaining_seconds} seconds before requesting a new OTP"
        super().__init__(detail=detail)


class OTPRateLimitException(BaseHTTPException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Too many OTP requests. Try again in 1 hour"


class OTPExpiredOrNotFoundException(OTPException):
    detail = "OTP expired or not found"


class OTPIncorrectException(OTPException):
    detail = "Incorrect code"


class OTPVerifyAttemptsExceededException(BaseHTTPException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Too many failed verification attempts. Try again in 10 minutes"
