# Library Management System

A menu-driven Python application I built to manage a library's books, members, and borrowing records.


---

## What does it do?

I wanted to build something practical, so I chose a library system. It lets you:

- Add books to a catalog and search for them by title, author, genre, or ISBN
- Register library members with different membership types
- Borrow and return books, with due dates automatically set to 14 days
- Track overdue books and charge fines of €0.50 per day

All data is automatically saved to CSV files so nothing is lost when you close the program.

---

## File Structure

```
library-management-system/
│
├── main.py                  # Start here — runs the main menu
│
├── models/                  # The main classes
│   ├── book.py              # Book class
│   ├── user.py              # User class
│   ├── borrow_record.py     # Tracks each borrowing transaction
│   └── fine.py              # Tracks overdue fines
│
├── services/                # All the business logic
│   ├── book_service.py      # Adding, removing, searching books
│   ├── user_service.py      # Registering and managing members
│   └── borrow_service.py    # Borrowing, returning, and fines
│
├── menus/                   # What the user sees and interacts with
│   ├── book_menu.py         # Book catalog menu
│   ├── user_menu.py         # Member management menu
│   └── borrow_menu.py       # Borrowing and returns menu
│
├── utils/                   # Helper functions used across the project
│   ├── storage.py           # Reads and writes CSV files
│   ├── validators.py        # Checks user input is valid
│   └── display.py           # Makes the console output look nice
│
└── data/                    # CSV files are created here automatically
    ├── books.csv
    ├── users.csv
    ├── borrow_records.csv
    └── fines.csv
```

---


```bash
git clone https://github.com/Ahsan4022/library-management-system.git
cd library-management-system
python main.py
```

---

## Example

```
  MAIN MENU
  1. Book Catalog
  2. Member Management
  3. Borrowing & Returns
  0. Exit

  → Your choice: 3

  BORROWING & RETURNS
  1. Borrow a book

  → Your choice: 1
  → User ID: U001
  → Book ISBN: 9780451524935
  ✔  Book borrowed successfully!
  ℹ  [R001] User:U001 | ISBN:9780451524935 | Due:2026-07-10 | Status:active
```

---

## Features

| Feature | How it works |
|---|---|
| Book catalog | You can add, update, remove, and search books |
| Copy tracking | Keeps track of how many copies are available |
| Membership tiers | Standard members can borrow 3 books, Student 5, Premium 10 |
| Borrowing | Books are due back after 14 days |
| Overdue detection | The system checks for overdue books every time it starts |
| Fines | €0.50 is charged for each day a book is overdue |
| CSV storage | Everything is saved to simple CSV files you can open in Excel |
| Error handling | If something goes wrong, a clear error message is shown |

---

## Python concepts I used

| Concept | Where I used it |
|---|---|
| Classes and Objects | Book, User, BorrowRecord, and Fine in the models folder |
| Methods | Every class has multiple methods for different actions |
| Loops and conditionals | Used throughout the menus and services |
| File I/O | storage.py reads and writes all data to CSV files |
| Exception handling | try/except blocks catch errors in all menu actions |
| Modules and packages | Code is split across models, services, menus, and utils |
| Comments | Added to explain what each part of the code does |

---

## Author

Muhammad Ahsan Tahir — Gisma University of Applied Sciences  
Roll Number: GH1050837  
Module: B100C Python Programming
