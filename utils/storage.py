"""
utils/storage.py
"""

import csv
import os


DATA_DIR = "data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def _file_path(filename):
    return os.path.join(DATA_DIR, filename)


def load_csv(filename, factory):
    path = _file_path(filename)
    if not os.path.exists(path):
        return []
    records = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(factory(row))
    return records


def save_csv(filename, records, fieldnames):
    path = _file_path(filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_dict())


def append_csv(filename, record, fieldnames):
    path = _file_path(filename)
    write_header = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(record.to_dict())


def generate_id(prefix, existing_ids):
    numbers = []
    for id_ in existing_ids:
        try:
            numbers.append(int(id_.lstrip(prefix)))
        except ValueError:
            pass
    if numbers:
        next_num = max(numbers) + 1
    else:
        next_num = 1
    return f"{prefix}{next_num:03d}"