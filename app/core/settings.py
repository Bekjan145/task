from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE: str
    REDIS_URL: str

    OTP_LENGTH: int = 4
    OTP_MIN_VALUE: int = 1000
    OTP_MAX_VALUE: int = 9999
    OTP_EXPIRE_MINUTES: int = 5
    OTP_COOLDOWN_SECONDS: int = 60
    OTP_MAX_ATTEMPTS: int = 5
    OTP_MAX_ATTEMPTS_WINDOW: int = 3600
    OTP_MAX_VERIFY_ATTEMPTS: int = 3
    OTP_VERIFY_ATTEMPTS_WINDOW: int = 600

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
