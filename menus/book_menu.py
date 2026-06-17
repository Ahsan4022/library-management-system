"""
menus/book_menu.py
------------------
Interactive CLI sub-menu for book catalog management.
"""

from services.book_service import BookService
from utils import display as ui


def run(book_svc: BookService) -> None:
    """Display and handle the Book Management sub-menu loop.

    Args:
        book_svc: Shared BookService instance.
    """
    while True:
        ui.header("Book Management")
        print("  1. List all books")
        print("  2. List available books")
        print("  3. Search books")
        print("  4. Add a book")
        print("  5. Update book details")
        print("  6. Remove a book")
        print("  0. Back to main menu")

        choice = ui.prompt("Your choice")

        if choice == "1":
            _list_all(book_svc)
        elif choice == "2":
            _list_available(book_svc)
        elif choice == "3":
            _search(book_svc)
        elif choice == "4":
            _add_book(book_svc)
        elif choice == "5":
            _update_book(book_svc)
        elif choice == "6":
            _remove_book(book_svc)
        elif choice == "0":
            break
        else:
            ui.error("Invalid option. Please try again.")


# ------------------------------------------------------------------
# Sub-handlers
# ------------------------------------------------------------------

def _list_all(svc: BookService) -> None:
    ui.header("All Books")
    ui.listing(svc.list_all(), "The catalog is empty.")


def _list_available(svc: BookService) -> None:
    ui.header("Available Books")
    ui.listing(svc.list_available(), "No books currently available.")


def _search(svc: BookService) -> None:
    ui.header("Search Books")
    field = ui.prompt("Search by (title/author/genre/isbn) [default: title]") or "title"
    query = ui.prompt("Search query")
    if not query:
        ui.error("Search query cannot be empty.")
        return
    try:
        results = svc.search(query, field)
        ui.listing(results, f"No books matched '{query}'.")
    except ValueError as exc:
        ui.error(str(exc))


def _add_book(svc: BookService) -> None:
    ui.header("Add Book")
    isbn = ui.prompt("ISBN")
    title = ui.prompt("Title")
    author = ui.prompt("Author")
    genre = ui.prompt("Genre")
    year_str = ui.prompt("Publication year")
    copies_str = ui.prompt("Number of copies [default: 1]") or "1"

    try:
        book = svc.add_book(
            isbn=isbn,
            title=title,
            author=author,
            genre=genre,
            year=int(year_str),
            copies=int(copies_str),
        )
        ui.success(f"Book added: {book}")
    except (ValueError, RuntimeError) as exc:
        ui.error(str(exc))


def _update_book(svc: BookService) -> None:
    ui.header("Update Book")
    isbn = ui.prompt("ISBN of book to update")
    book = svc.get_book(isbn)
    if book is None:
        ui.error(f"No book found with ISBN '{isbn}'.")
        return

    ui.info(f"Current details: {book}")
    updates = {}
    for field, label in [("title", "New title"), ("author", "New author"),
                          ("genre", "New genre"), ("year", "New year")]:
        val = ui.prompt(f"{label} [leave blank to keep]")
        if val:
            updates[field] = int(val) if field == "year" else val

    if not updates:
        ui.info("No changes made.")
        return

    try:
        updated = svc.update_book(isbn, **updates)
        ui.success(f"Updated: {updated}")
    except (ValueError, KeyError) as exc:
        ui.error(str(exc))


def _remove_book(svc: BookService) -> None:
    ui.header("Remove Book")
    isbn = ui.prompt("ISBN of book to remove")
    book = svc.get_book(isbn)
    if book is None:
        ui.error(f"No book found with ISBN '{isbn}'.")
        return

    ui.info(f"About to remove: {book}")
    if ui.confirm("Are you sure?"):
        try:
            svc.remove_book(isbn)
            ui.success("Book removed successfully.")
        except RuntimeError as exc:
            ui.error(str(exc))
    else:
        ui.info("Removal cancelled.")
