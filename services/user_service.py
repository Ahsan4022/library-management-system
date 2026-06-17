"""
services/user_service.py
------------------------
Business logic layer for library member management.
"""

from typing import Dict, List, Optional

from models.user import User
from utils.storage import load_csv, save_csv, generate_id
from utils.validators import validate_email, validate_non_empty

# CSV configuration
_FILE = "users.csv"
_FIELDS = [
    "user_id", "name", "email", "phone", "membership_type",
    "is_active", "registered_on", "active_loans",
]


class UserService:
    """CRUD and query operations for library members.

    The user registry is persisted in a CSV file and mirrored in memory
    as a dictionary keyed by user_id for O(1) look-ups.
    """

    def __init__(self) -> None:
        """Load user records from CSV."""
        users: List[User] = load_csv(_FILE, User.from_dict)
        self._users: Dict[str, User] = {u.user_id: u for u in users}

    # ------------------------------------------------------------------
    # Internal persistence
    # ------------------------------------------------------------------

    def _persist(self) -> None:
        """Write the in-memory registry to the CSV file."""
        save_csv(_FILE, list(self._users.values()), _FIELDS)

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def register_user(
        self,
        name: str,
        email: str,
        phone: str,
        membership_type: str = "standard",
    ) -> User:
        """Register a new library member.

        Args:
            name: Full name.
            email: Contact e-mail address.
            phone: Contact phone number.
            membership_type: 'standard', 'student', or 'premium'.

        Returns:
            User: Newly created User instance.

        Raises:
            ValueError: If email format is invalid or required fields are empty.
        """
        if not validate_non_empty(name):
            raise ValueError("User name must not be empty.")
        if not validate_email(email):
            raise ValueError(f"Invalid email address: '{email}'")
        if email in {u.email for u in self._users.values()}:
            raise ValueError(f"A user with email '{email}' is already registered.")

        user_id = generate_id("U", list(self._users.keys()))
        user = User(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            membership_type=membership_type,
        )
        self._users[user_id] = user
        self._persist()
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve a user by ID (returns None on miss).

        Args:
            user_id: User identifier string.

        Returns:
            User | None: The User if found, else None.
        """
        return self._users.get(user_id)

    def find_by_email(self, email: str) -> Optional[User]:
        """Find a user by their e-mail address.

        Args:
            email: E-mail to search for.

        Returns:
            User | None: Matched user or None.
        """
        email_lower = email.lower()
        for user in self._users.values():
            if user.email.lower() == email_lower:
                return user
        return None

    def update_contact(
        self,
        user_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> User:
        """Update a user's contact details.

        Args:
            user_id: ID of the user to update.
            email: New e-mail (optional).
            phone: New phone number (optional).

        Returns:
            User: Updated user instance.

        Raises:
            KeyError: If user_id is not found.
            ValueError: If email format is invalid.
        """
        user = self._get_or_raise(user_id)
        if email and not validate_email(email):
            raise ValueError(f"Invalid email address: '{email}'")
        user.update_contact(email=email, phone=phone)
        self._persist()
        return user

    def upgrade_membership(self, user_id: str, new_type: str) -> User:
        """Change a user's membership tier.

        Args:
            user_id: ID of the user.
            new_type: Target membership type.

        Returns:
            User: Updated user instance.

        Raises:
            KeyError: If user_id is not found.
            ValueError: If new_type is invalid.
        """
        user = self._get_or_raise(user_id)
        user.upgrade_membership(new_type)
        self._persist()
        return user

    def deactivate_user(self, user_id: str) -> User:
        """Deactivate a user's account.

        Args:
            user_id: ID of the user.

        Returns:
            User: Updated user instance.

        Raises:
            KeyError: If user_id is not found.
            RuntimeError: If the user still has active loans.
        """
        user = self._get_or_raise(user_id)
        if user.active_loans > 0:
            raise RuntimeError(
                f"Cannot deactivate '{user.name}': {user.active_loans} active loan(s)."
            )
        user.deactivate()
        self._persist()
        return user

    def activate_user(self, user_id: str) -> User:
        """Reactivate a deactivated account.

        Args:
            user_id: ID of the user.

        Returns:
            User: Reactivated user instance.

        Raises:
            KeyError: If user_id is not found.
        """
        user = self._get_or_raise(user_id)
        user.activate()
        self._persist()
        return user

    # ------------------------------------------------------------------
    # Loan counters (called by BorrowService)
    # ------------------------------------------------------------------

    def increment_loans(self, user_id: str) -> None:
        """Increment a user's active loan count.

        Args:
            user_id: ID of the user.

        Raises:
            KeyError: If user_id is not found.
        """
        self._get_or_raise(user_id).increment_loans()
        self._persist()

    def decrement_loans(self, user_id: str) -> None:
        """Decrement a user's active loan count.

        Args:
            user_id: ID of the user.

        Raises:
            KeyError: If user_id is not found.
        """
        self._get_or_raise(user_id).decrement_loans()
        self._persist()

    # ------------------------------------------------------------------
    # Listing and search
    # ------------------------------------------------------------------

    def list_all(self) -> List[User]:
        """Return all users sorted by name.

        Returns:
            List[User]: Every registered user.
        """
        return sorted(self._users.values(), key=lambda u: u.name.lower())

    def list_active(self) -> List[User]:
        """Return only active users, sorted by name.

        Returns:
            List[User]: Active users.
        """
        return sorted(
            (u for u in self._users.values() if u.is_active),
            key=lambda u: u.name.lower(),
        )

    def search_by_name(self, query: str) -> List[User]:
        """Case-insensitive substring search over user names.

        Args:
            query: Search term.

        Returns:
            List[User]: Matching users sorted by name.
        """
        q = query.lower()
        return sorted(
            (u for u in self._users.values() if q in u.name.lower()),
            key=lambda u: u.name.lower(),
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_or_raise(self, user_id: str) -> User:
        """Return a user by ID or raise KeyError.

        Args:
            user_id: ID to look up.

        Returns:
            User: Found user.

        Raises:
            KeyError: If no user with this ID exists.
        """
        user = self._users.get(user_id)
        if user is None:
            raise KeyError(f"No user found with ID '{user_id}'.")
        return user
