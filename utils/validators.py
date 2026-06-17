"""
utils/validators.py
-------------------
Input-validation helpers used throughout the service layer.
"""

import re
from datetime import datetime


def validate_isbn(isbn: str) -> bool:
    """Check that an ISBN-10 or ISBN-13 string is syntactically valid.

    Args:
        isbn (str): ISBN string (hyphens are stripped before checking).

    Returns:
        bool: True if valid, False otherwise.
    """
    cleaned = isbn.replace("-", "").replace(" ", "")
    return bool(re.fullmatch(r"\d{10}|\d{13}", cleaned))


def validate_email(email: str) -> bool:
    """Basic RFC-5322-lite e-mail format check.

    Args:
        email (str): E-mail address to validate.

    Returns:
        bool: True if the string looks like a valid e-mail address.
    """
    pattern = r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$"
    return bool(re.fullmatch(pattern, email))


def validate_year(year: int) -> bool:
    """Validate a publication year.

    Accepts any year from 1 AD up to and including the current year,
    covering ancient texts (Homer, Virgil, etc.) through contemporary works.

    Args:
        year (int): Publication year (positive integer).

    Returns:
        bool: True if 1 <= year <= current_year.
    """
    current_year = datetime.now().year
    return 1 <= year <= current_year


def validate_positive_int(value: int) -> bool:
    """Ensure a value is a positive integer.

    Args:
        value (int): Value to check.

    Returns:
        bool: True if value >= 1.
    """
    return isinstance(value, int) and value >= 1


def validate_non_empty(value: str) -> bool:
    """Ensure a string is non-empty after stripping whitespace.

    Args:
        value (str): String to check.

    Returns:
        bool: True if the stripped value is non-empty.
    """
    return bool(value and value.strip())
