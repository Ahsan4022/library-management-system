"""
main.py
-------
Entry point for the Library Management System.

Run with:
    python main.py
"""

import sys

from services.book_service import BookService
from services.user_service import UserService
from services.borrow_service import BorrowService
from menus import book_menu, user_menu, borrow_menu
from utils import display as ui


def _bootstrap() -> tuple[BookService, UserService, BorrowService]:
    """Initialise all services; shared instances flow as dependencies.

    Returns:
        Tuple of (BookService, UserService, BorrowService).
    """
    book_svc = BookService()
    user_svc = UserService()
    borrow_svc = BorrowService(book_svc, user_svc)
    return book_svc, user_svc, borrow_svc


def main() -> None:
    """Top-level menu loop for the Library Management System."""
    try:
        book_svc, user_svc, borrow_svc = _bootstrap()
    except Exception as exc:  # noqa: BLE001 – startup failures are fatal
        print(f"[FATAL] Failed to initialise services: {exc}", file=sys.stderr)
        sys.exit(1)

    ui.header("Welcome to the Library Management System")
    ui.info("All data is persisted in the 'data/' directory as CSV files.")

    while True:
        print("\n" + "─" * 60)
        print("  MAIN MENU")
        print("─" * 60)
        print("  1. Book Catalog")
        print("  2. Member Management")
        print("  3. Borrowing & Returns")
        print("  0. Exit")
        print("─" * 60)

        choice = ui.prompt("Your choice")

        if choice == "1":
            book_menu.run(book_svc)
        elif choice == "2":
            user_menu.run(user_svc)
        elif choice == "3":
            borrow_menu.run(borrow_svc)
        elif choice == "0":
            ui.info("Goodbye!")
            break
        else:
            ui.error("Invalid option. Please enter 1, 2, 3, or 0.")


if __name__ == "__main__":
    main()
