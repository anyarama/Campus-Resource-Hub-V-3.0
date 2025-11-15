"""Form validation helpers."""
from __future__ import annotations

import re
from typing import Tuple

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def validate_string(value: str, min_length: int, max_length: int, label: str) -> Tuple[bool, str]:
    if not value:
        return False, f'{label} is required.'
    if len(value) < min_length:
        return False, f'{label} must be at least {min_length} characters.'
    if len(value) > max_length:
        return False, f'{label} must be under {max_length} characters.'
    return True, ''


def validate_email(value: str) -> bool:
    return bool(value and EMAIL_REGEX.match(value))


def validate_password(value: str) -> Tuple[bool, str]:
    if len(value) < 8:
        return False, 'Password must contain at least eight characters.'
    if not re.search(r'[A-Z]', value):
        return False, 'Include at least one uppercase letter.'
    if not re.search(r'[a-z]', value):
        return False, 'Include at least one lowercase letter.'
    if not re.search(r'[0-9]', value):
        return False, 'Include at least one digit.'
    return True, ''


def validate_integer(value: str | int, minimum: int, maximum: int, label: str):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return False, f'{label} must be a whole number.'
    if number < minimum or number > maximum:
        return False, f'{label} must be between {minimum} and {maximum}.'
    return True, number


class Validator:
    """Convenience wrapper offering class-style access."""

    validate_string = staticmethod(validate_string)
    validate_email = staticmethod(validate_email)
    validate_password = staticmethod(validate_password)
    validate_integer = staticmethod(validate_integer)
