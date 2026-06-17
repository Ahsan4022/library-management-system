"""
services/book_service.py
------------------------
Business logic layer for book catalog management.
"""

from typing import Dict, List, Optional

from models.book import Book
from utils.storage import load_csv, save_csv
from utils.validators import validate_isbn, validate_year, validate_non_empty

# CSV configuration
_FILE = "books.csv"
_FIELDS = [
    "isbn", "title", "author", "genre", "year",
    "copies_total", "copies_available", "added_on",
]


class BookService:
    """CRUD and search operations for the library's book catalog.

    Books are loaded from CSV on construction and written back after every
    mutating operation so the in-memory state is always in sync with disk.
    """

    def __init__(self) -> None:
        """Load the book catalog from CSV into an in-memory dictionary."""
        books: List[Book] = load_csv(_FILE, Book.from_dict)
        self._catalog: Dict[str, Book] = {b.isbn: b for b in books}

    # ------------------------------------------------------------------
    # Internal persistence
    # ------------------------------------------------------------------

    def _persist(self) -> None:
        """Write the current in-memory catalog to the CSV file."""
        save_csv(_FILE, list(self._catalog.values()), _FIELDS)

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def add_book(
        self,
        isbn: str,
        title: str,
        author: str,
        genre: str,
        year: int,
        copies: int = 1,
    ) -> Book:
        """Add a new book (or increase copy count for an existing ISBN).

        Args:
            isbn: ISBN-10 or ISBN-13 identifier.
            title: Book title.
            author: Author's full name.
            genre: Genre/category string.
            year: Publication year.
            copies: Number of copies to add (default 1).

        Returns:
            Book: The created or updated Book instance.

        Raises:
            ValueError: On invalid ISBN, year, or empty required fields.
        """
        if not validate_isbn(isbn):
            raise ValueError(f"Invalid ISBN format: '{isbn}'")
        if not validate_year(year):
            raise ValueError(f"Year {year} is out of acceptable range.")
        if not validate_non_empty(title):
            raise ValueError("Book title must not be empty.")
        if not validate_non_empty(author):
            raise ValueError("Author name must not be empty.")

        if isbn in self._catalog:
            # Increase copies of existing book
            book = self._catalog[isbn]
            book.copies_total += copies
            book.copies_available += copies
        else:
            book = Book(
                isbn=isbn,
                title=title,
                author=author,
                genre=genre,
                year=year,
                copies_total=copies,
                copies_available=copies,
            )
            self._catalog[isbn] = book

        self._persist()
        return book

    def remove_book(self, isbn: str) -> Book:
        """Remove a book from the catalog.

        Args:
            isbn: ISBN of the book to remove.

        Returns:
            Book: The removed Book instance.

        Raises:
            KeyError: If the ISBN is not in the catalog.
            RuntimeError: If copies are still on loan.
        """
        book = self._get_or_raise(isbn)
        on_loan = book.copies_total - book.copies_available
        if on_loan > 0:
            raise RuntimeError(
                f"Cannot remove '{book.title}': {on_loan} cop(ies) still on loan."
            )
        del self._catalog[isbn]
        self._persist()
        return book

    def update_book(self, isbn: str, **kwargs) -> Book:
        """Update one or more fields of an existing book.

        Accepted keyword arguments: title, author, genre, year.

        Args:
            isbn: ISBN of the book to update.
            **kwargs: Field name → new value pairs.

        Returns:
            Book: Updated Book instance.

        Raises:
            KeyError: If the ISBN is not found.
            ValueError: On invalid field values.
        """
        book = self._get_or_raise(isbn)
        if "year" in kwargs and not validate_year(int(kwargs["year"])):
            raise ValueError(f"Year {kwargs['year']} is out of acceptable range.")
        book.update_details(**kwargs)
        self._persist()
        return book

    def get_book(self, isbn: str) -> Optional[Book]:
        """Retrieve a book by ISBN without raising on miss.

        Args:
            isbn: ISBN to look up.

        Returns:
            Book | None: The Book if found, otherwise None.
        """
        return self._catalog.get(isbn)

    # ------------------------------------------------------------------
    # Search and listing
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        field: str = "title",
    ) -> List[Book]:
        """Case-insensitive substring search over the catalog.

        Args:
            query: Search term.
            field: One of 'title', 'author', 'genre', 'isbn' (default 'title').

        Returns:
            List[Book]: Matching books sorted by title.

        Raises:
            ValueError: If *field* is not a searchable attribute.
        """
        searchable = {"title", "author", "genre", "isbn"}
        if field not in searchable:
            raise ValueError(f"Cannot search by '{field}'. Use one of {searchable}.")

        q = query.lower()
        results = [
            b for b in self._catalog.values()
            if q in getattr(b, field, "").lower()
        ]
        return sorted(results, key=lambda b: b.title.lower())

    def list_available(self) -> List[Book]:
        """Return all books that have at least one available copy.

        Returns:
            List[Book]: Available books sorted alphabetically by title.
        """
        return sorted(
            (b for b in self._catalog.values() if b.is_available()),
            key=lambda b: b.title.lower(),
        )

    def list_all(self) -> List[Book]:
        """Return every book in the catalog, sorted by title.

        Returns:
            List[Book]: All books.
        """
        return sorted(self._catalog.values(), key=lambda b: b.title.lower())

    # ------------------------------------------------------------------
    # Checkout / check-in (called by BorrowService)
    # ------------------------------------------------------------------

    def checkout_copy(self, isbn: str) -> None:
        """Reserve one copy of a book (called during borrowing).

        Args:
            isbn: ISBN of the book to check out.

        Raises:
            KeyError: If the ISBN is unknown.
            RuntimeError: If no copies are currently available.
        """
        book = self._get_or_raise(isbn)
        if not book.checkout():
            raise RuntimeError(f"No available copies of '{book.title}' (ISBN: {isbn}).")
        self._persist()

    def checkin_copy(self, isbn: str) -> None:
        """Release one copy of a book (called during return).

        Args:
            isbn: ISBN of the book being returned.

        Raises:
            KeyError: If the ISBN is unknown.
        """
        book = self._get_or_raise(isbn)
        book.checkin()
        self._persist()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_or_raise(self, isbn: str) -> Book:
        """Return a book by ISBN or raise KeyError.

        Args:
            isbn: ISBN to look up.

        Returns:
            Book: Found book.

        Raises:
            KeyError: If no book with this ISBN exists.
        """
        book = self._catalog.get(isbn)
        if book is None:
            raise KeyError(f"No book found with ISBN '{isbn}'.")
        return book
