import csv
import os, sys
from pathlib import Path
from typing import Optional
from stat_functions import stats_path

def add_info(label: str, info, filename: str) -> None:
    """
    Adds info under the given label (column) in the specified CSV file.
    If the label does not exist, it creates the column and adds the info.
    If the label exists, it adds the info to the last incomplete row.
    Multiple calls will fill the same row horizontally until all columns are filled,
    then a new row is started.
    Creates the file if it does not exist.
    """
    ROOT_DIR = Path(__file__).resolve().parents[3]
    base_root = ROOT_DIR / "src" / "exp2" / "stats_data"
    # stats_path.stats_folder should be like "experiment{datetime}\testcase{datetime}"
    if stats_path.stats_folder:
        base_path = base_root / stats_path.stats_folder
    else:
        base_path = base_root

    file_path = base_path / filename
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file_exists = os.path.exists(file_path)
    rows = []
    fieldnames = []

    if file_exists and os.path.getsize(file_path) > 0:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames if reader.fieldnames else []
            rows = list(reader)
    else:
        fieldnames = []

    # Add label if not present
    if label not in fieldnames:
        fieldnames.append(label)
        # Add empty value for new label in all previous rows
        for row in rows:
            row[label] = ""

    # Find the last incomplete row (not all columns filled)
    target_row = None
    for row in reversed(rows):
        if row[label] == "":
            target_row = row
            break
        # If all columns are filled, continue

    # If no incomplete row, create a new one
    if target_row is None or all(row[col] != "" for col in fieldnames):
        new_row = {col: "" for col in fieldnames}
        new_row[label] = info
        rows.append(new_row)
    else:
        target_row[label] = info

    # Write back to file
    with open(file_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)