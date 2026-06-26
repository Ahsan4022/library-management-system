"""
models/book.py
"""

from datetime import datetime


class Book:
    """A book in the library."""

    def __init__(self, isbn, title, author, genre, year, copies_total, copies_available):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year
        self.copies_total = copies_total
        self.copies_available = copies_available
        self.added_on = datetime.now().isoformat()

    def checkout(self):
        if self.copies_available > 0:
            self.copies_available -= 1
            return True
        return False

    def checkin(self):
        if self.copies_available < self.copies_total:
            self.copies_available += 1
            return True
        return False

    def is_available(self):
        return self.copies_available > 0

    def update_details(self, title=None, author=None, genre=None, year=None):
        if title is not None:
            self.title = title
        if author is not None:
            self.author = author
        if genre is not None:
            self.genre = genre
        if year is not None:
            self.year = year

    def to_dict(self):
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "year": self.year,
            "copies_total": self.copies_total,
            "copies_available": self.copies_available,
            "added_on": self.added_on,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            isbn=data["isbn"],
            title=data["title"],
            author=data["author"],
            genre=data["genre"],
            year=int(data["year"]),
            copies_total=int(data["copies_total"]),
            copies_available=int(data["copies_available"]),
        )

    def __str__(self):
        return f"[{self.isbn}] '{self.title}' by {self.author} ({self.year}, {self.genre}) — {self.copies_available}/{self.copies_total} available"