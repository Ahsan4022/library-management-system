"""
models/user.py
"""

from datetime import datetime


class User:
    """A library member."""

    def __init__(self, user_id, name, email, phone, membership_type="standard"):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.membership_type = membership_type
        self.is_active = True
        self.registered_on = datetime.now().isoformat()
        self.active_loans = 0
        self.limits = {"standard": 3, "student": 5, "premium": 10}

    def borrow_limit(self):
        return self.limits.get(self.membership_type, 3)

    def can_borrow(self):
        return self.is_active and self.active_loans < self.borrow_limit()

    def increment_loans(self):
        self.active_loans += 1

    def decrement_loans(self):
        if self.active_loans > 0:
            self.active_loans -= 1

    def deactivate(self):
        self.is_active = False

    def activate(self):
        self.is_active = True

    def update_contact(self, email=None, phone=None):
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone

    def upgrade_membership(self, new_type):
        valid = ["standard", "student", "premium"]
        if new_type not in valid:
            raise ValueError("Invalid membership type.")
        self.membership_type = new_type

    def to_dict(self):
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
    def from_dict(cls, data):
        user = cls(
            user_id=data["user_id"],
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            membership_type=data.get("membership_type", "standard"),
        )
        user.is_active = data.get("is_active", "True") in ("True", "true", "1")
        user.registered_on = data.get("registered_on", datetime.now().isoformat())
        user.active_loans = int(data.get("active_loans", 0))
        return user

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"[{self.user_id}] {self.name} | {self.membership_type} | {self.email} | Loans: {self.active_loans}/{self.borrow_limit()} | {status}"