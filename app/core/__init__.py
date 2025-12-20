from app.core.settings import settings
from app.core.security import (
    get_current_user,
    create_access_token,
    create_refresh_token,
    verify_token_payload,
    hash_password,
    verify_password,
)
from app.core.redis_client import get_redis, init_redis, close_redis
from app.core.exceptions import (
    # Auth exceptions
    AuthException,
    InvalidCredentialsException,
    TokenInvalidException,
    TokenRevokedException,
    InvalidTokenTypeException,
    # User exceptions
    UserNotFoundException,
    PhoneAlreadyExistsException,
    InvalidPhoneFormatException,
    # Permission exceptions
    AccessDeniedException,
    AdminAccessRequiredException,
    # OTP exceptions
    OTPException,
    OTPCooldownException,
    OTPRateLimitException,
    OTPExpiredOrNotFoundException,
    OTPIncorrectException,
    OTPVerifyAttemptsExceededException,
)