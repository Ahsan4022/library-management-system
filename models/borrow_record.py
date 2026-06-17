"""
models/borrow_record.py
-----------------------
Defines the BorrowRecord class that tracks every borrowing transaction.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


# Default lending period in days
DEFAULT_LOAN_DAYS: int = 14
DAILY_FINE_RATE: float = 0.50  # EUR per overdue day


@dataclass
class BorrowRecord:
    """Represents a single book-borrowing transaction.

    Attributes:
        record_id (str): Unique transaction identifier.
        user_id (str): ID of the borrowing user.
        isbn (str): ISBN of the borrowed book.
        borrow_date (str): ISO-format date/time of borrowing.
        due_date (str): ISO-format date/time the book is due back.
        return_date (str | None): ISO-format actual return date, or None if still on loan.
        fine_amount (float): Fine accrued for late return (EUR).
        status (str): 'active', 'returned', or 'overdue'.
    """

    record_id: str
    user_id: str
    isbn: str
    borrow_date: str = field(default_factory=lambda: datetime.now().isoformat())
    due_date: str = field(
        default_factory=lambda: (
            datetime.now() + timedelta(days=DEFAULT_LOAN_DAYS)
        ).isoformat()
    )
    return_date: Optional[str] = None
    fine_amount: float = 0.0
    status: str = "active"

    # ------------------------------------------------------------------
    # Business logic
    # ------------------------------------------------------------------

    def process_return(self) -> float:
        """Mark the record as returned and calculate any overdue fine.

        Returns:
            float: Fine amount in EUR (0.0 if returned on time).
        """
        now = datetime.now()
        self.return_date = now.isoformat()
        due = datetime.fromisoformat(self.due_date)

        if now > due:
            overdue_days = (now - due).days or 1  # at least 1 day if past due
            self.fine_amount = round(overdue_days * DAILY_FINE_RATE, 2)
            self.status = "returned"
        else:
            self.fine_amount = 0.0
            self.status = "returned"

        return self.fine_amount

    def is_overdue(self) -> bool:
        """Determine whether this loan is currently overdue.

        Returns:
            bool: True if status is active and current time is past due_date.
        """
        if self.status != "active":
            return False
        return datetime.now() > datetime.fromisoformat(self.due_date)

    def days_overdue(self) -> int:
        """Calculate how many days overdue this active loan is.

        Returns:
            int: Number of days past due (0 if not overdue or already returned).
        """
        if not self.is_overdue():
            return 0
        return (datetime.now() - datetime.fromisoformat(self.due_date)).days

    def refresh_status(self) -> None:
        """Synchronise the status field with the current date (active → overdue)."""
        if self.status == "active" and self.is_overdue():
            self.status = "overdue"

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize the BorrowRecord for CSV persistence.

        Returns:
            dict: All fields as plain Python types.
        """
        return {
            "record_id": self.record_id,
            "user_id": self.user_id,
            "isbn": self.isbn,
            "borrow_date": self.borrow_date,
            "due_date": self.due_date,
            "return_date": self.return_date or "",
            "fine_amount": self.fine_amount,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BorrowRecord":
        """Deserialize a BorrowRecord from a CSV row dictionary.

        Args:
            data (dict): Row from csv.DictReader.

        Returns:
            BorrowRecord: Populated instance.
        """
        return cls(
            record_id=data["record_id"],
            user_id=data["user_id"],
            isbn=data["isbn"],
            borrow_date=data["borrow_date"],
            due_date=data["due_date"],
            return_date=data["return_date"] or None,
            fine_amount=float(data.get("fine_amount", 0.0)),
            status=data.get("status", "active"),
        )

    def __str__(self) -> str:
        ret = self.return_date or "Not returned"
        fine = f"Fine: €{self.fine_amount:.2f}" if self.fine_amount else ""
        return (
            f"[{self.record_id}] User:{self.user_id} | ISBN:{self.isbn} | "
            f"Borrowed:{self.borrow_date[:10]} | Due:{self.due_date[:10]} | "
            f"Return:{ret} | Status:{self.status} {fine}"
        ).rstrip()
