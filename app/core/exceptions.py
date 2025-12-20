from fastapi import HTTPException, status


class AuthException(HTTPException):
    """Base authentication exception"""
    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(status_code=status_code, detail=detail)


class InvalidCredentialsException(AuthException):
    def __init__(self):
        super().__init__(detail="Invalid phone or password")


class TokenInvalidException(AuthException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(detail=detail)


class TokenRevokedException(AuthException):
    def __init__(self):
        super().__init__(detail="Token revoked")


class InvalidTokenTypeException(AuthException):
    def __init__(self):
        super().__init__(detail="Invalid token type")


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


class PhoneAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already registered")


class InvalidPhoneFormatException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format. Expected format: +998901234567 or 901234567"
        )


class AccessDeniedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


class AdminAccessRequiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


class OTPException(HTTPException):
    """Base OTP exception"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class OTPCooldownException(HTTPException):
    def __init__(self, remaining_seconds: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Please wait {remaining_seconds} seconds before requesting a new OTP"
        )


class OTPRateLimitException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP requests. Try again in 1 hour"
        )


class OTPExpiredOrNotFoundException(OTPException):
    def __init__(self):
        super().__init__(detail="OTP expired or not found")


class OTPIncorrectException(OTPException):
    def __init__(self):
        super().__init__(detail="Incorrect code")


class OTPVerifyAttemptsExceededException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed verification attempts. Try again in 10 minutes"
        )