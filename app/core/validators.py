import re

from app.core.exceptions import InvalidPhoneFormatException


def validate_phone(phone: str) -> None:
    cleaned = re.sub(r'[\s\-\(\)]+', '', phone)

    uz_pattern = r'^(?:\+998|998)?([0-9]{9})$'

    if not re.match(uz_pattern, cleaned):
        raise InvalidPhoneFormatException()


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


def process_phone(phone: str) -> str:
    validate_phone(phone)
    return normalize_phone(phone)
