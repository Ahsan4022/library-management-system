"""
tests/test_user.py
------------------
Unit tests for the User model.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from models.user import User


@pytest.fixture
def standard_user() -> User:
    return User(
        user_id="U001",
        name="Alice Müller",
        email="alice@example.com",
        phone="+49123456789",
        membership_type="standard",
    )


@pytest.fixture
def premium_user() -> User:
    return User(
        user_id="U002",
        name="Bob Schmidt",
        email="bob@example.com",
        phone="+49987654321",
        membership_type="premium",
    )


class TestBorrowLimit:
    def test_standard_limit(self, standard_user):
        assert standard_user.borrow_limit() == 3

    def test_premium_limit(self, premium_user):
        assert premium_user.borrow_limit() == 10

    def test_student_limit(self):
        user = User("U003", "Carl", "carl@x.com", "+491111", membership_type="student")
        assert user.borrow_limit() == 5


class TestCanBorrow:
    def test_can_borrow_when_under_limit(self, standard_user):
        standard_user.active_loans = 2
        assert standard_user.can_borrow() is True

    def test_cannot_borrow_at_limit(self, standard_user):
        standard_user.active_loans = 3
        assert standard_user.can_borrow() is False

    def test_cannot_borrow_when_inactive(self, standard_user):
        standard_user.is_active = False
        assert standard_user.can_borrow() is False


class TestLoanCounters:
    def test_increment_loans(self, standard_user):
        standard_user.increment_loans()
        assert standard_user.active_loans == 1

    def test_decrement_loans(self, standard_user):
        standard_user.active_loans = 2
        standard_user.decrement_loans()
        assert standard_user.active_loans == 1

    def test_decrement_does_not_go_below_zero(self, standard_user):
        standard_user.active_loans = 0
        standard_user.decrement_loans()
        assert standard_user.active_loans == 0


class TestMembershipUpgrade:
    def test_valid_upgrade(self, standard_user):
        standard_user.upgrade_membership("premium")
        assert standard_user.membership_type == "premium"

    def test_invalid_type_raises(self, standard_user):
        with pytest.raises(ValueError):
            standard_user.upgrade_membership("vip")


class TestActivation:
    def test_deactivate(self, standard_user):
        standard_user.deactivate()
        assert standard_user.is_active is False

    def test_activate(self, standard_user):
        standard_user.is_active = False
        standard_user.activate()
        assert standard_user.is_active is True


class TestSerialization:
    def test_roundtrip(self, standard_user):
        data = standard_user.to_dict()
        restored = User.from_dict(data)
        assert restored.user_id == standard_user.user_id
        assert restored.membership_type == standard_user.membership_type
        assert restored.active_loans == standard_user.active_loans
