"""
tests/test_services_integration.py
------------------------------------
Integration tests for BookService, UserService, and BorrowService.
Uses a temporary data directory so no real CSV files are touched.
"""

import sys
import os
import shutil
import tempfile
import pytest

# Redirect DATA_DIR before importing services
_TMP = tempfile.mkdtemp()
os.environ["LIBRARY_DATA_DIR"] = _TMP
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Patch the DATA_DIR in storage module
import utils.storage as _storage
from pathlib import Path
_storage.DATA_DIR = Path(_TMP)

from services.book_service import BookService
from services.user_service import UserService
from services.borrow_service import BorrowService


@pytest.fixture(autouse=True)
def clean_tmp():
    """Clear all CSV files between tests."""
    yield
    for f in Path(_TMP).glob("*.csv"):
        f.unlink()


@pytest.fixture
def book_svc():
    return BookService()


@pytest.fixture
def user_svc():
    return UserService()


@pytest.fixture
def borrow_svc(book_svc, user_svc):
    return BorrowService(book_svc, user_svc)


# ------------------------------------------------------------------
# BookService tests
# ------------------------------------------------------------------

class TestBookService:
    def test_add_and_retrieve_book(self, book_svc):
        book = book_svc.add_book("9780140449136", "The Odyssey", "Homer", "Epic", 800)
        assert book_svc.get_book("9780140449136") is not None

    def test_add_duplicate_isbn_increases_copies(self, book_svc):
        book_svc.add_book("9780140449136", "The Odyssey", "Homer", "Epic", 800, copies=1)
        book_svc.add_book("9780140449136", "The Odyssey", "Homer", "Epic", 800, copies=2)
        book = book_svc.get_book("9780140449136")
        assert book.copies_total == 3

    def test_invalid_isbn_raises(self, book_svc):
        with pytest.raises(ValueError):
            book_svc.add_book("BADISBN", "Title", "Author", "Genre", 2020)

    def test_search_by_title(self, book_svc):
        book_svc.add_book("9780140449136", "The Odyssey", "Homer", "Epic", 800)
        results = book_svc.search("odyssey", "title")
        assert len(results) == 1

    def test_remove_book(self, book_svc):
        book_svc.add_book("9780140449136", "The Odyssey", "Homer", "Epic", 800)
        book_svc.remove_book("9780140449136")
        assert book_svc.get_book("9780140449136") is None

    def test_remove_nonexistent_raises(self, book_svc):
        with pytest.raises(KeyError):
            book_svc.remove_book("0000000000000")


# ------------------------------------------------------------------
# UserService tests
# ------------------------------------------------------------------

class TestUserService:
    def test_register_user(self, user_svc):
        user = user_svc.register_user("Alice", "alice@x.com", "+491234")
        assert user.user_id.startswith("U")
        assert user_svc.get_user(user.user_id) is not None

    def test_duplicate_email_raises(self, user_svc):
        user_svc.register_user("Alice", "alice@x.com", "+491234")
        with pytest.raises(ValueError):
            user_svc.register_user("Alice2", "alice@x.com", "+495678")

    def test_invalid_email_raises(self, user_svc):
        with pytest.raises(ValueError):
            user_svc.register_user("Bob", "not-an-email", "+491234")

    def test_upgrade_membership(self, user_svc):
        user = user_svc.register_user("Alice", "alice@x.com", "+491234")
        user_svc.upgrade_membership(user.user_id, "premium")
        assert user_svc.get_user(user.user_id).membership_type == "premium"

    def test_deactivate_with_loans_raises(self, user_svc):
        user = user_svc.register_user("Bob", "bob@x.com", "+495678")
        user_svc.increment_loans(user.user_id)
        with pytest.raises(RuntimeError):
            user_svc.deactivate_user(user.user_id)


# ------------------------------------------------------------------
# BorrowService integration tests
# ------------------------------------------------------------------

class TestBorrowService:
    def _setup(self, book_svc, user_svc):
        book = book_svc.add_book("9780140449136", "Odyssey", "Homer", "Epic", 800)
        user = user_svc.register_user("Alice", "alice@x.com", "+491234")
        return book, user

    def test_borrow_and_return(self, borrow_svc, book_svc, user_svc):
        book, user = self._setup(book_svc, user_svc)
        record = borrow_svc.borrow_book(user.user_id, book.isbn)
        assert record.status == "active"
        # Book copy count reduced
        assert book_svc.get_book(book.isbn).copies_available == 0
        # Return
        returned_record, fine = borrow_svc.return_book(record.record_id)
        assert returned_record.status == "returned"
        assert fine is None  # returned within due date
        # Copy restored
        assert book_svc.get_book(book.isbn).copies_available == 1

    def test_cannot_borrow_unavailable_book(self, borrow_svc, book_svc, user_svc):
        book, user = self._setup(book_svc, user_svc)
        borrow_svc.borrow_book(user.user_id, book.isbn)  # takes the only copy
        user2 = user_svc.register_user("Bob", "bob@x.com", "+495678")
        with pytest.raises(RuntimeError):
            borrow_svc.borrow_book(user2.user_id, book.isbn)

    def test_cannot_exceed_borrow_limit(self, borrow_svc, book_svc, user_svc):
        user = user_svc.register_user("Carl", "carl@x.com", "+496789")
        # Add 4 books, standard limit is 3
        for i in range(4):
            isbn = f"978014044913{i}"
            book_svc.add_book(isbn, f"Book {i}", "Author", "Genre", 2020)
            if i < 3:
                borrow_svc.borrow_book(user.user_id, isbn)

        with pytest.raises(RuntimeError, match="borrow limit"):
            borrow_svc.borrow_book(user.user_id, "9780140449133")

    def test_return_already_returned_raises(self, borrow_svc, book_svc, user_svc):
        book, user = self._setup(book_svc, user_svc)
        record = borrow_svc.borrow_book(user.user_id, book.isbn)
        borrow_svc.return_book(record.record_id)
        with pytest.raises(RuntimeError, match="already marked"):
            borrow_svc.return_book(record.record_id)

    def test_overdue_loan_detection(self, borrow_svc, book_svc, user_svc):
        from datetime import datetime, timedelta
        book, user = self._setup(book_svc, user_svc)
        record = borrow_svc.borrow_book(user.user_id, book.isbn)
        # Manually set a past due date while keeping status active
        record.due_date = (datetime.now() - timedelta(days=3)).isoformat()
        record.status = "active"  # reset so is_overdue() check fires
        assert record.is_overdue() is True
        # After refresh the status should update to 'overdue'
        record.refresh_status()
        assert record.status == "overdue"

    def test_pay_fine(self, borrow_svc, book_svc, user_svc):
        from datetime import datetime, timedelta
        book, user = self._setup(book_svc, user_svc)
        record = borrow_svc.borrow_book(user.user_id, book.isbn)
        record.due_date = (datetime.now() - timedelta(days=5)).isoformat()
        _, fine = borrow_svc.return_book(record.record_id)
        assert fine is not None
        paid_fine = borrow_svc.pay_fine(fine.fine_id)
        assert paid_fine.is_paid is True
