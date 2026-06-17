"""
tests/test_borrow_record.py
---------------------------
Unit tests for the BorrowRecord model.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import datetime, timedelta
from models.borrow_record import BorrowRecord


@pytest.fixture
def active_record() -> BorrowRecord:
    future_due = (datetime.now() + timedelta(days=7)).isoformat()
    return BorrowRecord(
        record_id="R001",
        user_id="U001",
        isbn="9780140449136",
        due_date=future_due,
    )


@pytest.fixture
def overdue_record() -> BorrowRecord:
    past_due = (datetime.now() - timedelta(days=5)).isoformat()
    return BorrowRecord(
        record_id="R002",
        user_id="U001",
        isbn="9780140449136",
        due_date=past_due,
        status="active",
    )


class TestIsOverdue:
    def test_not_overdue_within_period(self, active_record):
        assert active_record.is_overdue() is False

    def test_overdue_past_due_date(self, overdue_record):
        assert overdue_record.is_overdue() is True

    def test_returned_record_not_overdue(self, overdue_record):
        overdue_record.status = "returned"
        assert overdue_record.is_overdue() is False


class TestDaysOverdue:
    def test_days_overdue_positive(self, overdue_record):
        assert overdue_record.days_overdue() >= 5

    def test_days_overdue_zero_when_not_late(self, active_record):
        assert active_record.days_overdue() == 0


class TestProcessReturn:
    def test_return_on_time_no_fine(self, active_record):
        fine = active_record.process_return()
        assert fine == 0.0
        assert active_record.status == "returned"
        assert active_record.return_date is not None

    def test_return_late_incurs_fine(self, overdue_record):
        fine = overdue_record.process_return()
        assert fine > 0.0
        assert overdue_record.status == "returned"


class TestRefreshStatus:
    def test_refresh_marks_overdue(self, overdue_record):
        overdue_record.refresh_status()
        assert overdue_record.status == "overdue"

    def test_refresh_does_not_change_on_time(self, active_record):
        active_record.refresh_status()
        assert active_record.status == "active"


class TestSerialization:
    def test_roundtrip(self, active_record):
        data = active_record.to_dict()
        restored = BorrowRecord.from_dict(data)
        assert restored.record_id == active_record.record_id
        assert restored.status == active_record.status
        assert restored.return_date == active_record.return_date
