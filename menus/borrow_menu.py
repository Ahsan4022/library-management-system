"""
menus/borrow_menu.py
"""

from services.borrow_service import BorrowService
from utils import display as ui


def run(borrow_svc):
    while True:
        ui.header("Borrowing & Returns")
        print("  1. Borrow a book")
        print("  2. Return a book")
        print("  3. View active loans")
        print("  4. View overdue loans")
        print("  5. View borrow history")
        print("  6. View outstanding fines")
        print("  7. Pay a fine")
        print("  8. Waive a fine")
        print("  0. Back to main menu")

        choice = ui.prompt("Your choice")

        if choice == "1":
            _borrow(borrow_svc)
        elif choice == "2":
            _return_book(borrow_svc)
        elif choice == "3":
            _active_loans(borrow_svc)
        elif choice == "4":
            _overdue_loans(borrow_svc)
        elif choice == "5":
            _history(borrow_svc)
        elif choice == "6":
            _outstanding_fines(borrow_svc)
        elif choice == "7":
            _pay_fine(borrow_svc)
        elif choice == "8":
            _waive_fine(borrow_svc)
        elif choice == "0":
            break
        else:
            ui.error("Invalid option.")


def _borrow(svc):
    ui.header("Borrow a Book")
    user_id = ui.prompt("User ID")
    isbn = ui.prompt("Book ISBN")
    try:
        record = svc.borrow_book(user_id, isbn)
        ui.success("Book borrowed successfully!")
        ui.info(str(record))
    except Exception as e:
        ui.error(str(e))


def _return_book(svc):
    ui.header("Return a Book")
    record_id = ui.prompt("Borrow Record ID")
    try:
        record, fine = svc.return_book(record_id)
        ui.success("Book returned successfully.")
        ui.info(str(record))
        if fine:
            ui.info("Overdue fine issued: " + str(fine))
        else:
            ui.info("No fine — returned on time.")
    except Exception as e:
        ui.error(str(e))


def _active_loans(svc):
    ui.header("Active Loans")
    uid = ui.prompt("Filter by User ID [blank for all]") or None
    ui.listing(svc.active_loans(uid), "No active loans.")


def _overdue_loans(svc):
    ui.header("Overdue Loans")
    overdue = svc.overdue_loans()
    if not overdue:
        ui.info("No overdue loans!")
        return
    for r in overdue:
        print("  " + str(r) + " (overdue by " + str(r.days_overdue()) + " day(s))")


def _history(svc):
    ui.header("Borrow History")
    uid = ui.prompt("Filter by User ID [blank for all]") or None
    ui.listing(svc.loan_history(uid), "No history found.")


def _outstanding_fines(svc):
    ui.header("Outstanding Fines")
    fines = svc.outstanding_fines()
    if not fines:
        ui.info("No outstanding fines.")
        return
    total = 0
    for f in fines:
        total += f.amount
    ui.listing(fines)
    print("\n  Total outstanding: €" + str(round(total, 2)))


def _pay_fine(svc):
    ui.header("Pay Fine")
    fine_id = ui.prompt("Fine ID")
    try:
        fine = svc.pay_fine(fine_id)
        ui.success("Fine " + fine.fine_id + " marked as paid!")
    except Exception as e:
        ui.error(str(e))


def _waive_fine(svc):
    ui.header("Waive Fine")
    fine_id = ui.prompt("Fine ID to waive")
    if ui.confirm("Confirm waiver?"):
        try:
            fine = svc.waive_fine(fine_id)
            ui.success("Fine " + fine.fine_id + " has been waived.")
        except Exception as e:
            ui.error(str(e))