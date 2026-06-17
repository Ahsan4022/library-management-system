# 📚 Library Management System

A modular, menu-driven Python application for managing a library's books, members, and borrowing records. Built for the B100 Introduction to Computer Programming with Python assessment at Gisma University of Applied Sciences.

---

## Project Purpose

The system automates core library operations:

- Maintaining a searchable book catalog with copy-level inventory tracking
- Registering and managing library members with tiered memberships
- Issuing and processing book loans with automatic due-date tracking
- Calculating and settling overdue fines at €0.50/day

---

## File Structure

```
library_system/
│
├── main.py                        # Entry point — top-level CLI menu
│
├── models/                        # Domain entities (pure data + behaviour)
│   ├── __init__.py
│   ├── book.py                    # Book class
│   ├── user.py                    # User class
│   ├── borrow_record.py           # BorrowRecord class
│   └── fine.py                    # Fine class
│
├── services/                      # Business logic layer
│   ├── __init__.py
│   ├── book_service.py            # Catalog CRUD & search
│   ├── user_service.py            # Member management
│   └── borrow_service.py          # Loans, returns & fines
│
├── menus/                         # Interactive CLI sub-menus
│   ├── __init__.py
│   ├── book_menu.py
│   ├── user_menu.py
│   └── borrow_menu.py
│
├── utils/                         # Shared helpers
│   ├── __init__.py
│   ├── storage.py                 # Generic CSV read/write
│   ├── validators.py              # Input validation functions
│   └── display.py                 # Console formatting helpers
│
├── data/                          # CSV persistence layer
│   ├── books.csv
│   ├── users.csv
│   ├── borrow_records.csv
│   └── fines.csv
│
└── tests/                         # Automated test suite
    ├── __init__.py
    ├── test_book.py
    ├── test_user.py
    ├── test_borrow_record.py
    └── test_services_integration.py
```

---

## Installation

**Requirements:** Python 3.10 or later (uses `match` in type hints). No third-party packages required.

```bash
# Clone the repository
git clone https://github.com/<your-username>/library-management-system.git
cd library-management-system

# (Optional) create and activate a virtual environment
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows

# No pip install needed — standard library only
```

---

## Running the Application

```bash
cd library_system
python main.py
```

---

## Example Usage

```
──────────────────────────────────────────────────────────────
  MAIN MENU
──────────────────────────────────────────────────────────────
  1. Book Catalog
  2. Member Management
  3. Borrowing & Returns
  0. Exit

  → Your choice: 3

──────────────────────────────────────────────────────────────
  BORROWING & RETURNS
──────────────────────────────────────────────────────────────
  1. Borrow a book
  ...

  → Your choice: 1
  → User ID: U001
  → Book ISBN: 9780451524935
  ✔  Book borrowed successfully!
  ℹ  [R001] User:U001 | ISBN:9780451524935 | Borrowed:2026-06-17 | Due:2026-07-01 | Status:active
```

---

## Key Features

| Feature | Detail |
|---|---|
| Book catalog | Add, update, remove, and search books by title/author/genre/ISBN |
| Inventory | Per-copy tracking; prevents over-issue |
| Membership tiers | Standard (3), Student (5), Premium (10) borrow limits |
| Borrow / return | Full lifecycle with automatic due-date assignment |
| Overdue detection | Status refreshed on every startup and return |
| Fines | Auto-calculated at €0.50/overdue day; pay or waive via menu |
| CSV persistence | All data stored in human-readable CSV files under `data/` |
| Exception handling | All user-facing errors caught and displayed gracefully |
| PEP 8 compliant | Full docstrings on every class and method |

---

## Running Tests

```bash
cd library_system
pip install pytest   # only dependency for tests
pytest tests/ -v
```

---

## Python Concepts Demonstrated

| Concept | Where |
|---|---|
| **Classes & Objects** | `models/book.py`, `models/user.py`, `models/borrow_record.py`, `models/fine.py` |
| **Methods (4+ per class)** | All model classes |
| **Control structures** | Loops & conditionals throughout services and menus |
| **File I/O** | `utils/storage.py` — CSV read/write/append |
| **Exception handling** | Service layer raises; menu layer catches and displays |
| **Modules & packages** | 5 packages (`models`, `services`, `menus`, `utils`, `tests`) |
| **PEP 8 & docstrings** | Every file, class, and function documented |
| **Dataclasses** | `@dataclass` decorator used on all model classes |
| **Type hints** | All function signatures annotated |

---

## Data Files

CSV files in `data/` are plain text and can be inspected or pre-populated manually. Sample data for 8 books and 4 users is included.

---

## Author

Student — Gisma University of Applied Sciences, School of Computer Science  
Module: B100 Introduction to Computer Programming with Python
