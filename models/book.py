"""
models/book.py
--------------
Defines the Book class representing a library book entity.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Book:
    """Represents a book in the library catalog.

    Attributes:
        isbn (str): Unique identifier for the book.
        title (str): Title of the book.
        author (str): Author's full name.
        genre (str): Genre/category of the book.
        year (int): Publication year.
        copies_total (int): Total number of copies owned.
        copies_available (int): Copies currently available for borrowing.
        added_on (str): ISO-format date the book was added to the system.
    """

    isbn: str
    title: str
    author: str
    genre: str
    year: int
    copies_total: int
    copies_available: int
    added_on: str = field(default_factory=lambda: datetime.now().isoformat())

    # ------------------------------------------------------------------
    # Inventory helpers
    # ------------------------------------------------------------------

    def checkout(self) -> bool:
        """Decrement available copies when a book is borrowed.

        Returns:
            bool: True if a copy was successfully checked out, False if none available.
        """
        if self.copies_available > 0:
            self.copies_available -= 1
            return True
        return False

    def checkin(self) -> bool:
        """Increment available copies when a book is returned.

        Returns:
            bool: True on success, False if copies_available already equals copies_total.
        """
        if self.copies_available < self.copies_total:
            self.copies_available += 1
            return True
        return False

    def is_available(self) -> bool:
        """Check whether at least one copy is available.

        Returns:
            bool: True if copies_available > 0.
        """
        return self.copies_available > 0

    def update_details(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
    ) -> None:
        """Update one or more book fields in place.

        Args:
            title: New title (optional).
            author: New author name (optional).
            genre: New genre (optional).
            year: New publication year (optional).
        """
        if title is not None:
            self.title = title
        if author is not None:
            self.author = author
        if genre is not None:
            self.genre = genre
        if year is not None:
            self.year = year

    def to_dict(self) -> dict:
        """Serialize the Book to a plain dictionary (for CSV persistence).

        Returns:
            dict: All fields as strings/ints suitable for csv.DictWriter.
        """
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
    def from_dict(cls, data: dict) -> "Book":
        """Deserialize a Book from a dictionary (e.g., a CSV row).

        Args:
            data (dict): Row with string values as read from csv.DictReader.

        Returns:
            Book: Populated Book instance.
        """
        return cls(
            isbn=data["isbn"],
            title=data["title"],
            author=data["author"],
            genre=data["genre"],
            year=int(data["year"]),
            copies_total=int(data["copies_total"]),
            copies_available=int(data["copies_available"]),
            added_on=data.get("added_on", datetime.now().isoformat()),
        )

    def __str__(self) -> str:
        availability = (
            f"{self.copies_available}/{self.copies_total} available"
        )
        return (
            f"[{self.isbn}] '{self.title}' by {self.author} "
            f"({self.year}, {self.genre}) — {availability}"
        )
