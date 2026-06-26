"""
menus/book_menu.py
"""

from services.book_service import BookService
from utils import display as ui


def run(book_svc):
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
            ui.listing(book_svc.list_all(), "No books found.")
        elif choice == "2":
            ui.listing(book_svc.list_available(), "No available books.")
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
            ui.error("Invalid option.")


def _search(svc):
    field = ui.prompt("Search by (title/author/genre/isbn)") or "title"
    query = ui.prompt("Search query")
    if not query:
        ui.error("Query cannot be empty.")
        return
    results = svc.search(query, field)
    ui.listing(results, "No books found.")


def _add_book(svc):
    ui.header("Add Book")
    isbn = ui.prompt("ISBN")
    title = ui.prompt("Title")
    author = ui.prompt("Author")
    genre = ui.prompt("Genre")
    year_str = ui.prompt("Publication year")
    copies_str = ui.prompt("Number of copies [default: 1]") or "1"

    try:
        book = svc.add_book(isbn, title, author, genre, int(year_str), int(copies_str))
        ui.success("Book added: " + str(book))
    except Exception as e:
        ui.error(str(e))


def _update_book(svc):
    ui.header("Update Book")
    isbn = ui.prompt("ISBN of book to update")
    book = svc.get_book(isbn)
    if book is None:
        ui.error("Book not found.")
        return

    ui.info("Current: " + str(book))
    updates = {}
    title = ui.prompt("New title [blank to keep]")
    author = ui.prompt("New author [blank to keep]")
    genre = ui.prompt("New genre [blank to keep]")
    year = ui.prompt("New year [blank to keep]")

    if title:
        updates["title"] = title
    if author:
        updates["author"] = author
    if genre:
        updates["genre"] = genre
    if year:
        updates["year"] = int(year)

    if not updates:
        ui.info("No changes made.")
        return

    try:
        updated = svc.update_book(isbn, **updates)
        ui.success("Updated: " + str(updated))
    except Exception as e:
        ui.error(str(e))


def _remove_book(svc):
    ui.header("Remove Book")
    isbn = ui.prompt("ISBN of book to remove")
    book = svc.get_book(isbn)
    if book is None:
        ui.error("Book not found.")
        return

    ui.info("About to remove: " + str(book))
    if ui.confirm("Are you sure?"):
        try:
            svc.remove_book(isbn)
            ui.success("Book removed.")
        except Exception as e:
            ui.error(str(e))
    else:
        ui.info("Cancelled.")