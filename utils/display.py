"""
utils/display.py
"""


def header(title):
    print("\n" + "─" * 60)
    print("  " + title.upper())
    print("─" * 60)


def success(message):
    print("  ✔  " + message)


def error(message):
    print("  ✘  ERROR: " + message)


def info(message):
    print("  ℹ  " + message)


def listing(items, empty_msg="No records found."):
    if not items:
        info(empty_msg)
        return
    for idx, item in enumerate(items, start=1):
        print(f"  {idx}. {item}")


def prompt(text):
    return input("  → " + text + ": ").strip()


def confirm(question):
    answer = input("  ? " + question + " [y/N]: ").strip().lower()
    return answer in ("y", "yes")