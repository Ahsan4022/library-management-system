"""
services/book_service.py
"""

from models.book import Book
from utils.storage import load_csv, save_csv
from utils.validators import validate_isbn, validate_year, validate_non_empty


FILE = "books.csv"
FIELDS = ["isbn", "title", "author", "genre", "year", "copies_total", "copies_available", "added_on"]


class BookService:
    """Handles all book catalog operations."""

    def __init__(self):
        books = load_csv(FILE, Book.from_dict)
        self.catalog = {}
        for b in books:
            self.catalog[b.isbn] = b

    def _save(self):
        save_csv(FILE, list(self.catalog.values()), FIELDS)

    def add_book(self, isbn, title, author, genre, year, copies=1):
        if not validate_isbn(isbn):
            raise ValueError("Invalid ISBN.")
        if not validate_year(year):
            raise ValueError("Invalid year.")
        if not validate_non_empty(title):
            raise ValueError("Title cannot be empty.")
        if not validate_non_empty(author):
            raise ValueError("Author cannot be empty.")

        if isbn in self.catalog:
            self.catalog[isbn].copies_total += copies
            self.catalog[isbn].copies_available += copies
        else:
            book = Book(isbn, title, author, genre, year, copies, copies)
            self.catalog[isbn] = book

        self._save()
        return self.catalog[isbn]

    def remove_book(self, isbn):
        if isbn not in self.catalog:
            raise KeyError("Book not found.")
        book = self.catalog[isbn]
        on_loan = book.copies_total - book.copies_available
        if on_loan > 0:
            raise RuntimeError(f"Cannot remove — {on_loan} copy/copies still on loan.")
        del self.catalog[isbn]
        self._save()
        return book

    def update_book(self, isbn, **kwargs):
        if isbn not in self.catalog:
            raise KeyError("Book not found.")
        self.catalog[isbn].update_details(**kwargs)
        self._save()
        return self.catalog[isbn]

    def get_book(self, isbn):
        return self.catalog.get(isbn)

    def search(self, query, field="title"):
        results = []
        for book in self.catalog.values():
            value = getattr(book, field, "")
            if query.lower() in value.lower():
                results.append(book)
        return results

    def list_available(self):
        return [b for b in self.catalog.values() if b.is_available()]

    def list_all(self):
        return list(self.catalog.values())

    def checkout_copy(self, isbn):
        if isbn not in self.catalog:
            raise KeyError("Book not found.")
        if not self.catalog[isbn].checkout():
            raise RuntimeError("No available copies.")
        self._save()

    def checkin_copy(self, isbn):
        if isbn not in self.catalog:
            raise KeyError("Book not found.")
        self.catalog[isbn].checkin()
        self._save()