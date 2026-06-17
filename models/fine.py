"""
models/fine.py
--------------
Defines the Fine class for tracking outstanding and paid fines.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Fine:
    """Tracks a monetary fine associated with an overdue borrow record.

    Attributes:
        fine_id (str): Unique fine identifier.
        record_id (str): Linked BorrowRecord ID.
        user_id (str): ID of the user who owes the fine.
        amount (float): Fine amount in EUR.
        issued_on (str): ISO-format date the fine was issued.
        paid_on (str | None): ISO-format date of payment, or None if unpaid.
        is_paid (bool): Payment status flag.
    """

    fine_id: str
    record_id: str
    user_id: str
    amount: float
    issued_on: str = field(default_factory=lambda: datetime.now().isoformat())
    paid_on: Optional[str] = None
    is_paid: bool = False

    # ------------------------------------------------------------------
    # Payment management
    # ------------------------------------------------------------------

    def pay(self) -> None:
        """Mark the fine as paid and record the payment timestamp."""
        self.is_paid = True
        self.paid_on = datetime.now().isoformat()

    def waive(self) -> None:
        """Waive the fine (mark paid with zero enforcement action)."""
        self.amount = 0.0
        self.is_paid = True
        self.paid_on = datetime.now().isoformat()

    def apply_discount(self, percent: float) -> None:
        """Reduce the fine amount by a percentage.

        Args:
            percent (float): Discount percentage (0–100).

        Raises:
            ValueError: If percent is outside the [0, 100] range.
        """
        if not (0.0 <= percent <= 100.0):
            raise ValueError("Discount percent must be between 0 and 100.")
        self.amount = round(self.amount * (1 - percent / 100), 2)

    def outstanding_amount(self) -> float:
        """Return the outstanding fine amount.

        Returns:
            float: 0.0 if paid, else the full amount.
        """
        return 0.0 if self.is_paid else self.amount

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize the Fine for CSV persistence.

        Returns:
            dict: Plain types for csv.DictWriter.
        """
        return {
            "fine_id": self.fine_id,
            "record_id": self.record_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "issued_on": self.issued_on,
            "paid_on": self.paid_on or "",
            "is_paid": self.is_paid,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Fine":
        """Deserialize a Fine from a CSV row.

        Args:
            data (dict): Row from csv.DictReader.

        Returns:
            Fine: Populated instance.
        """
        return cls(
            fine_id=data["fine_id"],
            record_id=data["record_id"],
            user_id=data["user_id"],
            amount=float(data["amount"]),
            issued_on=data.get("issued_on", datetime.now().isoformat()),
            paid_on=data["paid_on"] or None,
            is_paid=data.get("is_paid", "False") in ("True", "true", "1"),
        )

    def __str__(self) -> str:
        status = "Paid" if self.is_paid else f"Outstanding (€{self.amount:.2f})"
        return (
            f"[{self.fine_id}] Record:{self.record_id} | User:{self.user_id} | "
            f"€{self.amount:.2f} | {status}"
        )
