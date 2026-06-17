"""
services/borrow_service.py
--------------------------
Business logic layer for borrowing, returning books, and managing fines.

This service orchestrates across BookService and UserService so that
borrow/return operations atomically update books, users, and records.
"""

from datetime import datetime
from typing import Dict, List, Optional

from models.borrow_record import BorrowRecord
from models.fine import Fine
from services.book_service import BookService
from services.user_service import UserService
from utils.storage import load_csv, save_csv, append_csv, generate_id

# CSV configuration – borrow records
_RECORDS_FILE = "borrow_records.csv"
_RECORDS_FIELDS = [
    "record_id", "user_id", "isbn", "borrow_date",
    "due_date", "return_date", "fine_amount", "status",
]

# CSV configuration – fines
_FINES_FILE = "fines.csv"
_FINES_FIELDS = [
    "fine_id", "record_id", "user_id", "amount",
    "issued_on", "paid_on", "is_paid",
]


class BorrowService:
    """Manages the full lifecycle of book loans.

    Responsibilities
    ----------------
    * Issue loans, preventing over-limit or unavailable-book situations.
    * Process returns, computing overdue fines automatically.
    * Track and settle outstanding fines.
    * Provide reporting queries (active loans, overdue items, fine summaries).

    Dependencies
    ------------
    Requires initialised ``BookService`` and ``UserService`` instances so that
    book availability and user loan counters are kept consistent.
    """

    def __init__(self, book_service: BookService, user_service: UserService) -> None:
        """Load borrow records and fines from CSV.

        Args:
            book_service: Shared book catalog service.
            user_service: Shared user registry service.
        """
        self._books = book_service
        self._users = user_service

        records: List[BorrowRecord] = load_csv(_RECORDS_FILE, BorrowRecord.from_dict)
        self._records: Dict[str, BorrowRecord] = {r.record_id: r for r in records}

        fines: List[Fine] = load_csv(_FINES_FILE, Fine.from_dict)
        self._fines: Dict[str, Fine] = {f.fine_id: f for f in fines}

        # Synchronise overdue statuses on startup
        self._refresh_all_statuses()

    # ------------------------------------------------------------------
    # Internal persistence
    # ------------------------------------------------------------------

    def _persist_records(self) -> None:
        """Rewrite the borrow_records CSV."""
        save_csv(_RECORDS_FILE, list(self._records.values()), _RECORDS_FIELDS)

    def _persist_fines(self) -> None:
        """Rewrite the fines CSV."""
        save_csv(_FINES_FILE, list(self._fines.values()), _FINES_FIELDS)

    # ------------------------------------------------------------------
    # Borrowing
    # ------------------------------------------------------------------

    def borrow_book(self, user_id: str, isbn: str) -> BorrowRecord:
        """Issue a book loan to a user.

        Args:
            user_id: ID of the borrowing user.
            isbn: ISBN of the desired book.

        Returns:
            BorrowRecord: The new loan record.

        Raises:
            KeyError: If user or book is not found.
            RuntimeError: If the user cannot borrow (inactive/at limit) or
                          no copies are available.
        """
        user = self._users.get_user(user_id)
        if user is None:
            raise KeyError(f"User '{user_id}' not found.")
        if not user.can_borrow():
            if not user.is_active:
                raise RuntimeError(f"User '{user.name}' account is inactive.")
            raise RuntimeError(
                f"User '{user.name}' has reached the borrow limit "
                f"({user.borrow_limit()} books)."
            )

        # Raises RuntimeError if no copies available, KeyError if ISBN unknown
        self._books.checkout_copy(isbn)

        record_id = generate_id("R", list(self._records.keys()))
        record = BorrowRecord(record_id=record_id, user_id=user_id, isbn=isbn)
        self._records[record_id] = record

        self._users.increment_loans(user_id)
        self._persist_records()
        return record

    # ------------------------------------------------------------------
    # Returns
    # ------------------------------------------------------------------

    def return_book(self, record_id: str) -> tuple[BorrowRecord, Optional[Fine]]:
        """Process the return of a borrowed book.

        Args:
            record_id: ID of the borrow record to close.

        Returns:
            Tuple of (BorrowRecord, Fine | None).  Fine is None when returned on time.

        Raises:
            KeyError: If the record is not found.
            RuntimeError: If the record is already closed.
        """
        record = self._get_record_or_raise(record_id)
        if record.status == "returned":
            raise RuntimeError(f"Record '{record_id}' is already marked as returned.")

        fine_amount = record.process_return()
        self._books.checkin_copy(record.isbn)
        self._users.decrement_loans(record.user_id)

        issued_fine: Optional[Fine] = None
        if fine_amount > 0.0:
            fine_id = generate_id("F", list(self._fines.keys()))
            issued_fine = Fine(
                fine_id=fine_id,
                record_id=record_id,
                user_id=record.user_id,
                amount=fine_amount,
            )
            self._fines[fine_id] = issued_fine
            self._persist_fines()

        self._persist_records()
        return record, issued_fine

    # ------------------------------------------------------------------
    # Fine management
    # ------------------------------------------------------------------

    def pay_fine(self, fine_id: str) -> Fine:
        """Mark a fine as paid.

        Args:
            fine_id: ID of the fine to settle.

        Returns:
            Fine: Updated Fine instance.

        Raises:
            KeyError: If the fine is not found.
            RuntimeError: If the fine is already paid.
        """
        fine = self._get_fine_or_raise(fine_id)
        if fine.is_paid:
            raise RuntimeError(f"Fine '{fine_id}' has already been paid.")
        fine.pay()
        self._persist_fines()
        return fine

    def waive_fine(self, fine_id: str) -> Fine:
        """Waive a fine (clear the amount and mark as paid).

        Args:
            fine_id: ID of the fine to waive.

        Returns:
            Fine: Updated Fine instance.

        Raises:
            KeyError: If the fine is not found.
        """
        fine = self._get_fine_or_raise(fine_id)
        fine.waive()
        self._persist_fines()
        return fine

    def get_user_fines(self, user_id: str) -> List[Fine]:
        """Return all fines associated with a user.

        Args:
            user_id: User identifier.

        Returns:
            List[Fine]: Fines sorted by issued date (newest first).
        """
        return sorted(
            (f for f in self._fines.values() if f.user_id == user_id),
            key=lambda f: f.issued_on,
            reverse=True,
        )

    def outstanding_fines(self) -> List[Fine]:
        """Return all unpaid fines across all users.

        Returns:
            List[Fine]: Unpaid fines sorted by issued date.
        """
        return sorted(
            (f for f in self._fines.values() if not f.is_paid),
            key=lambda f: f.issued_on,
        )

    # ------------------------------------------------------------------
    # Reporting / queries
    # ------------------------------------------------------------------

    def active_loans(self, user_id: Optional[str] = None) -> List[BorrowRecord]:
        """Return all active (not returned) loans, optionally filtered by user.

        Args:
            user_id: If supplied, filter to this user's loans.

        Returns:
            List[BorrowRecord]: Active loans sorted by due date.
        """
        records = [
            r for r in self._records.values()
            if r.status in ("active", "overdue")
            and (user_id is None or r.user_id == user_id)
        ]
        return sorted(records, key=lambda r: r.due_date)

    def overdue_loans(self) -> List[BorrowRecord]:
        """Return all loans that are currently past their due date.

        Returns:
            List[BorrowRecord]: Overdue records sorted by due date (oldest first).
        """
        return [r for r in self.active_loans() if r.is_overdue()]

    def loan_history(self, user_id: Optional[str] = None) -> List[BorrowRecord]:
        """Return the complete borrow history, optionally filtered by user.

        Args:
            user_id: If supplied, filter to this user only.

        Returns:
            List[BorrowRecord]: All records sorted by borrow date (newest first).
        """
        records = [
            r for r in self._records.values()
            if user_id is None or r.user_id == user_id
        ]
        return sorted(records, key=lambda r: r.borrow_date, reverse=True)

    def get_record(self, record_id: str) -> Optional[BorrowRecord]:
        """Retrieve a borrow record by ID.

        Args:
            record_id: Record identifier.

        Returns:
            BorrowRecord | None: The record if found, else None.
        """
        return self._records.get(record_id)

    # ------------------------------------------------------------------
    # Startup synchronisation
    # ------------------------------------------------------------------

    def _refresh_all_statuses(self) -> None:
        """Update status of all active records to 'overdue' if past due date."""
        changed = False
        for record in self._records.values():
            if record.status == "active" and record.is_overdue():
                record.status = "overdue"
                changed = True
        if changed:
            self._persist_records()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_record_or_raise(self, record_id: str) -> BorrowRecord:
        """Return a record by ID or raise KeyError.

        Args:
            record_id: Record ID to look up.

        Returns:
            BorrowRecord: Found record.

        Raises:
            KeyError: If not found.
        """
        record = self._records.get(record_id)
        if record is None:
            raise KeyError(f"No borrow record found with ID '{record_id}'.")
        return record

    def _get_fine_or_raise(self, fine_id: str) -> Fine:
        """Return a fine by ID or raise KeyError.

        Args:
            fine_id: Fine ID to look up.

        Returns:
            Fine: Found fine.

        Raises:
            KeyError: If not found.
        """
        fine = self._fines.get(fine_id)
        if fine is None:
            raise KeyError(f"No fine found with ID '{fine_id}'.")
        return fine
