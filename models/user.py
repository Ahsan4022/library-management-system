"""
models/user.py
--------------
Defines the User class representing a registered library member.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Represents a registered library member.

    Attributes:
        user_id (str): Unique member identifier (e.g., 'U001').
        name (str): Full name.
        email (str): Contact email address.
        phone (str): Contact phone number.
        membership_type (str): One of 'standard', 'student', or 'premium'.
        is_active (bool): Whether the account is active.
        registered_on (str): ISO-format date of registration.
        active_loans (int): Number of books currently on loan.
    """

    user_id: str
    name: str
    email: str
    phone: str
    membership_type: str = "standard"
    is_active: bool = True
    registered_on: str = field(default_factory=lambda: datetime.now().isoformat())
    active_loans: int = 0

    # Per-membership borrow limits
    _LIMITS: dict = field(default_factory=lambda: {
        "standard": 3,
        "student": 5,
        "premium": 10,
    }, init=False, repr=False)

    # ------------------------------------------------------------------
    # Loan tracking
    # ------------------------------------------------------------------

    def borrow_limit(self) -> int:
        """Return the maximum number of books this user may borrow simultaneously.

        Returns:
            int: Borrow limit based on membership_type.
        """
        return self._LIMITS.get(self.membership_type, 3)

    def can_borrow(self) -> bool:
        """Check whether the user is allowed to borrow another book.

        Returns:
            bool: True if active and under borrow limit.
        """
        return self.is_active and self.active_loans < self.borrow_limit()

    def increment_loans(self) -> None:
        """Increase the active_loans counter by one."""
        self.active_loans += 1

    def decrement_loans(self) -> None:
        """Decrease the active_loans counter by one (minimum 0)."""
        if self.active_loans > 0:
            self.active_loans -= 1

    # ------------------------------------------------------------------
    # Account management
    # ------------------------------------------------------------------

    def deactivate(self) -> None:
        """Deactivate the user's account."""
        self.is_active = False

    def activate(self) -> None:
        """Reactivate a previously deactivated account."""
        self.is_active = True

    def update_contact(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> None:
        """Update contact information.

        Args:
            email: New email address (optional).
            phone: New phone number (optional).
        """
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone

    def upgrade_membership(self, new_type: str) -> None:
        """Change the user's membership tier.

        Args:
            new_type (str): Target membership type ('standard', 'student', 'premium').

        Raises:
            ValueError: If new_type is not a valid membership tier.
        """
        valid = {"standard", "student", "premium"}
        if new_type not in valid:
            raise ValueError(
                f"Invalid membership type '{new_type}'. Choose from {valid}."
            )
        self.membership_type = new_type

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize the User to a plain dictionary for CSV persistence.

        Returns:
            dict: Field values suitable for csv.DictWriter.
        """
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "membership_type": self.membership_type,
            "is_active": self.is_active,
            "registered_on": self.registered_on,
            "active_loans": self.active_loans,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Deserialize a User from a dictionary (e.g., a CSV row).

        Args:
            data (dict): Row as read from csv.DictReader.

        Returns:
            User: Populated User instance.
        """
        return cls(
            user_id=data["user_id"],
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            membership_type=data.get("membership_type", "standard"),
            is_active=data.get("is_active", "True") in ("True", "true", "1"),
            registered_on=data.get("registered_on", datetime.now().isoformat()),
            active_loans=int(data.get("active_loans", 0)),
        )

    def __str__(self) -> str:
        status = "Active" if self.is_active else "Inactive"
        return (
            f"[{self.user_id}] {self.name} | {self.membership_type.capitalize()} | "
            f"{self.email} | Loans: {self.active_loans}/{self.borrow_limit()} | {status}"
        )
