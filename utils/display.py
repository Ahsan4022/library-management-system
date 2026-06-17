"""
utils/display.py
----------------
Console formatting helpers that keep the UI layer clean.
"""

from typing import List


SEPARATOR = "─" * 60


def header(title: str) -> None:
    """Print a styled section header.

    Args:
        title (str): Section title text.
    """
    print(f"\n{SEPARATOR}")
    print(f"  {title.upper()}")
    print(SEPARATOR)


def success(message: str) -> None:
    """Print a success message.

    Args:
        message (str): Success text.
    """
    print(f"  ✔  {message}")


def error(message: str) -> None:
    """Print an error message.

    Args:
        message (str): Error text.
    """
    print(f"  ✘  ERROR: {message}")


def info(message: str) -> None:
    """Print an informational message.

    Args:
        message (str): Info text.
    """
    print(f"  ℹ  {message}")


def listing(items: List, empty_msg: str = "No records found.") -> None:
    """Print a numbered list of items.

    Args:
        items (List): Objects with a ``__str__`` method.
        empty_msg (str): Message to display when *items* is empty.
    """
    if not items:
        info(empty_msg)
        return
    for idx, item in enumerate(items, start=1):
        print(f"  {idx:>3}. {item}")


def prompt(text: str) -> str:
    """Display an input prompt and return stripped user input.

    Args:
        text (str): Prompt label.

    Returns:
        str: Stripped response string.
    """
    return input(f"  → {text}: ").strip()


def confirm(question: str) -> bool:
    """Ask a yes/no question.

    Args:
        question (str): Question text.

    Returns:
        bool: True if the user responds 'y' or 'yes' (case-insensitive).
    """
    answer = input(f"  ? {question} [y/N]: ").strip().lower()
    return answer in ("y", "yes")
