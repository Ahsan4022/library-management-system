"""
menus/user_menu.py
------------------
Interactive CLI sub-menu for library member management.
"""

from services.user_service import UserService
from utils import display as ui


def run(user_svc: UserService) -> None:
    """Display and handle the User Management sub-menu loop.

    Args:
        user_svc: Shared UserService instance.
    """
    while True:
        ui.header("User Management")
        print("  1. List all members")
        print("  2. Search by name")
        print("  3. Register new member")
        print("  4. Update contact info")
        print("  5. Upgrade membership tier")
        print("  6. Deactivate member")
        print("  7. Reactivate member")
        print("  0. Back to main menu")

        choice = ui.prompt("Your choice")

        if choice == "1":
            ui.listing(user_svc.list_all(), "No members registered yet.")
        elif choice == "2":
            _search(user_svc)
        elif choice == "3":
            _register(user_svc)
        elif choice == "4":
            _update_contact(user_svc)
        elif choice == "5":
            _upgrade(user_svc)
        elif choice == "6":
            _deactivate(user_svc)
        elif choice == "7":
            _reactivate(user_svc)
        elif choice == "0":
            break
        else:
            ui.error("Invalid option.")


# ------------------------------------------------------------------
# Sub-handlers
# ------------------------------------------------------------------

def _search(svc: UserService) -> None:
    query = ui.prompt("Search name")
    ui.listing(svc.search_by_name(query), f"No members matched '{query}'.")


def _register(svc: UserService) -> None:
    ui.header("Register New Member")
    name = ui.prompt("Full name")
    email = ui.prompt("Email")
    phone = ui.prompt("Phone")
    mem = ui.prompt("Membership type (standard/student/premium) [default: standard]") or "standard"

    try:
        user = svc.register_user(name=name, email=email, phone=phone, membership_type=mem)
        ui.success(f"Member registered: {user}")
    except ValueError as exc:
        ui.error(str(exc))


def _update_contact(svc: UserService) -> None:
    uid = ui.prompt("User ID")
    user = svc.get_user(uid)
    if not user:
        ui.error(f"User '{uid}' not found.")
        return
    ui.info(f"Current: {user}")
    email = ui.prompt("New email [blank to keep]") or None
    phone = ui.prompt("New phone [blank to keep]") or None
    try:
        updated = svc.update_contact(uid, email=email, phone=phone)
        ui.success(f"Updated: {updated}")
    except (KeyError, ValueError) as exc:
        ui.error(str(exc))


def _upgrade(svc: UserService) -> None:
    uid = ui.prompt("User ID")
    tier = ui.prompt("New membership type (standard/student/premium)")
    try:
        updated = svc.upgrade_membership(uid, tier)
        ui.success(f"Membership updated: {updated}")
    except (KeyError, ValueError) as exc:
        ui.error(str(exc))


def _deactivate(svc: UserService) -> None:
    uid = ui.prompt("User ID to deactivate")
    if ui.confirm("Confirm deactivation?"):
        try:
            svc.deactivate_user(uid)
            ui.success("Account deactivated.")
        except (KeyError, RuntimeError) as exc:
            ui.error(str(exc))


def _reactivate(svc: UserService) -> None:
    uid = ui.prompt("User ID to reactivate")
    try:
        svc.activate_user(uid)
        ui.success("Account reactivated.")
    except KeyError as exc:
        ui.error(str(exc))
