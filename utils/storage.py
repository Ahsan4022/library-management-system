"""
utils/storage.py
----------------
Generic CSV persistence helpers used by all service layers.
"""

import csv
import os
from pathlib import Path
from typing import Callable, List, TypeVar

T = TypeVar("T")

# Ensure the data directory exists at import time
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _file_path(filename: str) -> Path:
    """Return the absolute path for a data file.

    Args:
        filename (str): Bare filename, e.g. 'books.csv'.

    Returns:
        Path: Full path inside the data directory.
    """
    return DATA_DIR / filename


def load_csv(filename: str, factory: Callable[[dict], T]) -> List[T]:
    """Load all rows from a CSV file and convert them via *factory*.

    Args:
        filename (str): Name of the CSV file (inside the data directory).
        factory (Callable): A ``from_dict`` class-method or equivalent callable
            that turns a ``dict`` row into a domain object.

    Returns:
        List[T]: Deserialized objects; empty list if the file does not exist.
    """
    path = _file_path(filename)
    if not path.exists():
        return []

    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return [factory(row) for row in reader]


def save_csv(filename: str, records: list, fieldnames: List[str]) -> None:
    """Persist *records* to a CSV file, overwriting any existing content.

    Args:
        filename (str): Name of the CSV file (inside the data directory).
        records (list): Domain objects that implement ``to_dict()``.
        fieldnames (List[str]): Ordered column headers for the CSV.
    """
    path = _file_path(filename)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_dict())


def append_csv(filename: str, record, fieldnames: List[str]) -> None:
    """Append a single *record* to a CSV file.

    Creates the file with a header row if it does not yet exist.

    Args:
        filename (str): Name of the CSV file (inside the data directory).
        record: Domain object implementing ``to_dict()``.
        fieldnames (List[str]): Ordered column headers for the CSV.
    """
    path = _file_path(filename)
    write_header = not path.exists() or os.path.getsize(path) == 0

    with path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(record.to_dict())


def generate_id(prefix: str, existing_ids: List[str]) -> str:
    """Generate the next sequential ID with the given *prefix*.

    Example: prefix='B', existing=['B001','B002'] → 'B003'

    Args:
        prefix (str): Single-character prefix letter.
        existing_ids (List[str]): All currently used IDs.

    Returns:
        str: New unique ID string.
    """
    numbers = []
    for id_ in existing_ids:
        try:
            numbers.append(int(id_.lstrip(prefix)))
        except ValueError:
            pass
    next_num = (max(numbers) + 1) if numbers else 1
    return f"{prefix}{next_num:03d}"
