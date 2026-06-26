"""
utils/validators.py
"""

from datetime import datetime


def validate_isbn(isbn):
    cleaned = isbn.replace("-", "").replace(" ", "")
    return len(cleaned) == 10 or len(cleaned) == 13


def validate_email(email):
    return "@" in email and "." in email.split("@")[-1]


def validate_year(year):
    current_year = datetime.now().year
    return 1 <= year <= current_year


def validate_positive_int(value):
    return isinstance(value, int) and value >= 1


def validate_non_empty(value):
    return bool(value and value.strip())