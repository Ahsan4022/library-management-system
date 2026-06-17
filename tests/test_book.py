"""
tests/test_book.py
------------------
Unit tests for the Book model.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from models.book import Book


@pytest.fixture
def sample_book() -> Book:
    return Book(
        isbn="9780140449136",
        title="The Odyssey",
        author="Homer",
        genre="Epic Poetry",
        year=800,
        copies_total=3,
        copies_available=3,
    )


class TestBookCheckout:
    def test_checkout_reduces_available(self, sample_book):
        sample_book.checkout()
        assert sample_book.copies_available == 2

    def test_checkout_returns_true_when_available(self, sample_book):
        assert sample_book.checkout() is True

    def test_checkout_returns_false_when_none_available(self, sample_book):
        sample_book.copies_available = 0
        assert sample_book.checkout() is False

    def test_checkout_does_not_go_below_zero(self, sample_book):
        sample_book.copies_available = 0
        sample_book.checkout()
        assert sample_book.copies_available == 0


class TestBookCheckin:
    def test_checkin_increases_available(self, sample_book):
        sample_book.copies_available = 1
        sample_book.checkin()
        assert sample_book.copies_available == 2

    def test_checkin_cannot_exceed_total(self, sample_book):
        result = sample_book.checkin()  # already at max
        assert result is False
        assert sample_book.copies_available == 3


class TestBookAvailability:
    def test_is_available_true(self, sample_book):
        assert sample_book.is_available() is True

    def test_is_available_false(self, sample_book):
        sample_book.copies_available = 0
        assert sample_book.is_available() is False


class TestBookUpdate:
    def test_update_title(self, sample_book):
        sample_book.update_details(title="Odyssey Updated")
        assert sample_book.title == "Odyssey Updated"

    def test_update_year(self, sample_book):
        sample_book.update_details(year=850)
        assert sample_book.year == 850

    def test_update_none_changes_nothing(self, sample_book):
        original_title = sample_book.title
        sample_book.update_details()
        assert sample_book.title == original_title


class TestBookSerialization:
    def test_to_dict_roundtrip(self, sample_book):
        data = sample_book.to_dict()
        restored = Book.from_dict(data)
        assert restored.isbn == sample_book.isbn
        assert restored.title == sample_book.title
        assert restored.copies_available == sample_book.copies_available

    def test_from_dict_handles_string_ints(self):
        data = {
            "isbn": "9780140449136",
            "title": "Test",
            "author": "Author",
            "genre": "Fiction",
            "year": "2020",
            "copies_total": "5",
            "copies_available": "3",
        }
        book = Book.from_dict(data)
        assert book.year == 2020
        assert book.copies_total == 5
