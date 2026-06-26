"""
menus/user_menu.py
"""

from services.user_service import UserService
from utils import display as ui


def run(user_svc):
    while True:
        ui.header("Member Management")
        print("  1. List all members")
        print("  2. Search by name")
        print("  3. Register new member")
        print("  4. Update contact info")
        print("  5. Upgrade membership")
        print("  6. Deactivate member")
        print("  7. Reactivate member")
        print("  0. Back to main menu")

        choice = ui.prompt("Your choice")

        if choice == "1":
            ui.listing(user_svc.list_all(), "No members found.")
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


def _search(svc):
    query = ui.prompt("Enter name to search")
    ui.listing(svc.search_by_name(query), "No members found.")


def _register(svc):
    ui.header("Register New Member")
    name = ui.prompt("Full name")
    email = ui.prompt("Email")
    phone = ui.prompt("Phone")
    mem = ui.prompt("Membership type (standard/student/premium) [default: standard]") or "standard"

    try:
        user = svc.register_user(name, email, phone, mem)
        ui.success("Member registered: " + str(user))
    except Exception as e:
        ui.error(str(e))


def _update_contact(svc):
    uid = ui.prompt("User ID")
    user = svc.get_user(uid)
    if user is None:
        ui.error("User not found.")
        return
    ui.info("Current: " + str(user))
    email = ui.prompt("New email [blank to keep]") or None
    phone = ui.prompt("New phone [blank to keep]") or None
    try:
        updated = svc.update_contact(uid, email=email, phone=phone)
        ui.success("Updated: " + str(updated))
    except Exception as e:
        ui.error(str(e))


def _upgrade(svc):
    uid = ui.prompt("User ID")
    tier = ui.prompt("New membership type (standard/student/premium)")
    try:
        updated = svc.upgrade_membership(uid, tier)
        ui.success("Membership updated: " + str(updated))
    except Exception as e:
        ui.error(str(e))


def _deactivate(svc):
    uid = ui.prompt("User ID to deactivate")
    if ui.confirm("Confirm deactivation?"):
        try:
            svc.deactivate_user(uid)
            ui.success("Account deactivated.")
        except Exception as e:
            ui.error(str(e))


def _reactivate(svc):
    uid = ui.prompt("User ID to reactivate")
    try:
        svc.activate_user(uid)
        ui.success("Account reactivated.")
    except Exception as e:
        ui.error(str(e))