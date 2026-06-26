"""
main.py
"""

from services.book_service import BookService
from services.user_service import UserService
from services.borrow_service import BorrowService
from menus import book_menu, user_menu, borrow_menu
from utils import display as ui


def main():
    try:
        book_svc = BookService()
        user_svc = UserService()
        borrow_svc = BorrowService(book_svc, user_svc)
    except Exception as e:
        print("Failed to start the system: " + str(e))
        return

    ui.header("Welcome to the Library Management System")
    print("  All data is saved in the data/ folder as CSV files.")

    while True:
        print("\n" + "─" * 60)
        print("  MAIN MENU")
        print("─" * 60)
        print("  1. Book Catalog")
        print("  2. Member Management")
        print("  3. Borrowing & Returns")
        print("  0. Exit")
        print("─" * 60)

        choice = input("  → Your choice: ").strip()

        if choice == "1":
            book_menu.run(book_svc)
        elif choice == "2":
            user_menu.run(user_svc)
        elif choice == "3":
            borrow_menu.run(borrow_svc)
        elif choice == "0":
            print("  Goodbye!")
            break
        else:
            print("  Invalid option. Please enter 1, 2, 3, or 0.")


if __name__ == "__main__":
    main()