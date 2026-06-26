"""
models/borrow_record.py
"""

from datetime import datetime, timedelta


DEFAULT_LOAN_DAYS = 14
DAILY_FINE_RATE = 0.50


class BorrowRecord:
    """A single borrowing transaction in the library."""

    def __init__(self, record_id, user_id, isbn, due_date=None):
        self.record_id = record_id
        self.user_id = user_id
        self.isbn = isbn
        self.borrow_date = datetime.now().isoformat()
        self.due_date = due_date or (datetime.now() + timedelta(days=DEFAULT_LOAN_DAYS)).isoformat()
        self.return_date = None
        self.fine_amount = 0.0
        self.status = "active"

    def process_return(self):
        # mark the book as returned and calculate fine if overdue
        now = datetime.now()
        self.return_date = now.isoformat()
        due = datetime.fromisoformat(self.due_date)
        if now > due:
            overdue_days = (now - due).days or 1
            self.fine_amount = round(overdue_days * DAILY_FINE_RATE, 2)
        else:
            self.fine_amount = 0.0
        self.status = "returned"
        return self.fine_amount

    def is_overdue(self):
        # check if the book is past its due date and not returned yet
        if self.status != "active":
            return False
        return datetime.now() > datetime.fromisoformat(self.due_date)

    def days_overdue(self):
        # return how many days past due this loan is
        if not self.is_overdue():
            return 0
        return (datetime.now() - datetime.fromisoformat(self.due_date)).days

    def refresh_status(self):
        # update status to overdue if past due date
        if self.status == "active" and self.is_overdue():
            self.status = "overdue"

    def to_dict(self):
        # convert to dictionary for saving to CSV
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
    def from_dict(cls, data):
        # create a BorrowRecord object from a CSV row
        record = cls(
            record_id=data["record_id"],
            user_id=data["user_id"],
            isbn=data["isbn"],
            due_date=data["due_date"],
        )
        record.borrow_date = data["borrow_date"]
        record.return_date = data["return_date"] or None
        record.fine_amount = float(data.get("fine_amount", 0.0))
        record.status = data.get("status", "active")
        return record

    def __str__(self):
        return (
            f"[{self.record_id}] User:{self.user_id} | ISBN:{self.isbn} | "
            f"Due:{self.due_date[:10]} | Status:{self.status}"
        )