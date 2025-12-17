import re
from fastapi import HTTPException, status


def validate_phone(phone: str) -> None:
    cleaned = re.sub(r'[\s\-\(\)]+', '', phone)

    uz_pattern = r'^(?:\+998|998)?([0-9]{9})$'

    if not re.match(uz_pattern, cleaned):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format. Expected format: +998901234567 or 901234567"
        )


def normalize_phone(phone: str) -> str:
    cleaned = re.sub(r'[\s\-\(\)]+', '', phone)

    if not cleaned.startswith('+'):
        if cleaned.startswith('998'):
            cleaned = '+' + cleaned
        elif cleaned.startswith('9'):
            cleaned = '+998' + cleaned
        else:
            cleaned = '+998' + cleaned

    return cleaned
