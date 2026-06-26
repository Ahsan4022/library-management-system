"""
models/fine.py
"""

from datetime import datetime


class Fine:
    """An overdue fine."""

    def __init__(self, fine_id, record_id, user_id, amount):
        self.fine_id = fine_id
        self.record_id = record_id
        self.user_id = user_id
        self.amount = amount
        self.issued_on = datetime.now().isoformat()
        self.paid_on = None
        self.is_paid = False

    def pay(self):
        self.is_paid = True
        self.paid_on = datetime.now().isoformat()

    def waive(self):
        self.amount = 0.0
        self.is_paid = True
        self.paid_on = datetime.now().isoformat()

    def apply_discount(self, percent):
        if percent < 0 or percent > 100:
            raise ValueError("Discount must be between 0 and 100.")
        self.amount = round(self.amount * (1 - percent / 100), 2)

    def outstanding_amount(self):
        if self.is_paid:
            return 0.0
        return self.amount

    def to_dict(self):
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
    def from_dict(cls, data):
        fine = cls(
            fine_id=data["fine_id"],
            record_id=data["record_id"],
            user_id=data["user_id"],
            amount=float(data["amount"]),
        )
        fine.issued_on = data.get("issued_on", datetime.now().isoformat())
        fine.paid_on = data["paid_on"] or None
        fine.is_paid = data.get("is_paid", "False") in ("True", "true", "1")
        return fine

    def __str__(self):
        status = "Paid" if self.is_paid else f"Outstanding (€{self.amount:.2f})"
        return f"[{self.fine_id}] Record:{self.record_id} | User:{self.user_id} | €{self.amount:.2f} | {status}"