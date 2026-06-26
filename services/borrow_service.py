"""
services/borrow_service.py
"""

from models.borrow_record import BorrowRecord
from models.fine import Fine
from utils.storage import load_csv, save_csv, generate_id


RECORDS_FILE = "borrow_records.csv"
RECORDS_FIELDS = ["record_id", "user_id", "isbn", "borrow_date", "due_date", "return_date", "fine_amount", "status"]

FINES_FILE = "fines.csv"
FINES_FIELDS = ["fine_id", "record_id", "user_id", "amount", "issued_on", "paid_on", "is_paid"]


class BorrowService:
    """Handles borrowing, returning books and managing fines."""

    def __init__(self, book_service, user_service):
        self.books = book_service
        self.users = user_service

        records = load_csv(RECORDS_FILE, BorrowRecord.from_dict)
        self.records = {}
        for r in records:
            self.records[r.record_id] = r

        fines = load_csv(FINES_FILE, Fine.from_dict)
        self.fines = {}
        for f in fines:
            self.fines[f.fine_id] = f

        self._refresh_statuses()

    def _save_records(self):
        save_csv(RECORDS_FILE, list(self.records.values()), RECORDS_FIELDS)

    def _save_fines(self):
        save_csv(FINES_FILE, list(self.fines.values()), FINES_FIELDS)

    def _refresh_statuses(self):
        for record in self.records.values():
            if record.status == "active" and record.is_overdue():
                record.status = "overdue"
        self._save_records()

    def borrow_book(self, user_id, isbn):
        user = self.users.get_user(user_id)
        if user is None:
            raise KeyError("User not found.")
        if not user.can_borrow():
            if not user.is_active:
                raise RuntimeError("User account is inactive.")
            raise RuntimeError("User has reached the borrow limit.")

        self.books.checkout_copy(isbn)

        record_id = generate_id("R", list(self.records.keys()))
        record = BorrowRecord(record_id, user_id, isbn)
        self.records[record_id] = record

        self.users.increment_loans(user_id)
        self._save_records()
        return record

    def return_book(self, record_id):
        if record_id not in self.records:
            raise KeyError("Borrow record not found.")
        record = self.records[record_id]
        if record.status == "returned":
            raise RuntimeError("This book is already returned.")

        fine_amount = record.process_return()
        self.books.checkin_copy(record.isbn)
        self.users.decrement_loans(record.user_id)

        issued_fine = None
        if fine_amount > 0.0:
            fine_id = generate_id("F", list(self.fines.keys()))
            issued_fine = Fine(fine_id, record_id, record.user_id, fine_amount)
            self.fines[fine_id] = issued_fine
            self._save_fines()

        self._save_records()
        return record, issued_fine

    def pay_fine(self, fine_id):
        if fine_id not in self.fines:
            raise KeyError("Fine not found.")
        if self.fines[fine_id].is_paid:
            raise RuntimeError("Fine is already paid.")
        self.fines[fine_id].pay()
        self._save_fines()
        return self.fines[fine_id]

    def waive_fine(self, fine_id):
        if fine_id not in self.fines:
            raise KeyError("Fine not found.")
        self.fines[fine_id].waive()
        self._save_fines()
        return self.fines[fine_id]

    def get_user_fines(self, user_id):
        return [f for f in self.fines.values() if f.user_id == user_id]

    def outstanding_fines(self):
        return [f for f in self.fines.values() if not f.is_paid]

    def active_loans(self, user_id=None):
        results = []
        for r in self.records.values():
            if r.status in ("active", "overdue"):
                if user_id is None or r.user_id == user_id:
                    results.append(r)
        return results

    def overdue_loans(self):
        return [r for r in self.records.values() if r.is_overdue()]

    def loan_history(self, user_id=None):
        results = []
        for r in self.records.values():
            if user_id is None or r.user_id == user_id:
                results.append(r)
        return results

    def get_record(self, record_id):
        return self.records.get(record_id)