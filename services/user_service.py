"""
services/user_service.py
"""

from models.user import User
from utils.storage import load_csv, save_csv, generate_id
from utils.validators import validate_email, validate_non_empty


FILE = "users.csv"
FIELDS = ["user_id", "name", "email", "phone", "membership_type", "is_active", "registered_on", "active_loans"]


class UserService:
    """Handles all library member operations."""

    def __init__(self):
        users = load_csv(FILE, User.from_dict)
        self.users = {}
        for u in users:
            self.users[u.user_id] = u

    def _save(self):
        save_csv(FILE, list(self.users.values()), FIELDS)

    def register_user(self, name, email, phone, membership_type="standard"):
        if not validate_non_empty(name):
            raise ValueError("Name cannot be empty.")
        if not validate_email(email):
            raise ValueError("Invalid email address.")
        for u in self.users.values():
            if u.email == email:
                raise ValueError("Email already registered.")

        user_id = generate_id("U", list(self.users.keys()))
        user = User(user_id, name, email, phone, membership_type)
        self.users[user_id] = user
        self._save()
        return user

    def get_user(self, user_id):
        return self.users.get(user_id)

    def find_by_email(self, email):
        for user in self.users.values():
            if user.email.lower() == email.lower():
                return user
        return None

    def update_contact(self, user_id, email=None, phone=None):
        if user_id not in self.users:
            raise KeyError("User not found.")
        if email and not validate_email(email):
            raise ValueError("Invalid email address.")
        self.users[user_id].update_contact(email=email, phone=phone)
        self._save()
        return self.users[user_id]

    def upgrade_membership(self, user_id, new_type):
        if user_id not in self.users:
            raise KeyError("User not found.")
        self.users[user_id].upgrade_membership(new_type)
        self._save()
        return self.users[user_id]

    def deactivate_user(self, user_id):
        if user_id not in self.users:
            raise KeyError("User not found.")
        if self.users[user_id].active_loans > 0:
            raise RuntimeError("Cannot deactivate — user has active loans.")
        self.users[user_id].deactivate()
        self._save()
        return self.users[user_id]

    def activate_user(self, user_id):
        if user_id not in self.users:
            raise KeyError("User not found.")
        self.users[user_id].activate()
        self._save()
        return self.users[user_id]

    def increment_loans(self, user_id):
        if user_id not in self.users:
            raise KeyError("User not found.")
        self.users[user_id].increment_loans()
        self._save()

    def decrement_loans(self, user_id):
        if user_id not in self.users:
            raise KeyError("User not found.")
        self.users[user_id].decrement_loans()
        self._save()

    def list_all(self):
        return list(self.users.values())

    def list_active(self):
        return [u for u in self.users.values() if u.is_active]

    def search_by_name(self, query):
        results = []
        for user in self.users.values():
            if query.lower() in user.name.lower():
                results.append(user)
        return results