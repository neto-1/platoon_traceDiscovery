import csv
import os
from typing import Optional
from pathlib import Path


def add_platoon_stat(platoon_id: int,
                     total_events: int,
                     duration_time: float,
                     testcases_id: int,
                     csv_path: Optional[str] = None) -> int:
    """
    Append a row to a CSV file with auto-incrementing id (starting at 0).

    Columns: id, platoon_id, total_events, duration_time, testcases_id
    Returns the id written.
    """

    if csv_path is None:
        ROOT_DIR = Path(__file__).resolve().parents[3]

        base_dir = ROOT_DIR / "src" / "exp2" / "stats_data"

        csv_file = base_dir / "platoon_stats.csv"

        # ensure directory exists
        csv_file.parent.mkdir(parents=True, exist_ok=True)

    else:
        csv_file = Path(csv_path)

    fieldnames = [
        "id",
        "platoon_id",
        "total_events",
        "duration_time",
        "testcases_id"
    ]

    # Determine next id
    next_id = 0

    if csv_file.exists() and csv_file.stat().st_size > 0:

        with open(csv_file, newline="", encoding="utf-8") as f:

            reader = csv.DictReader(f)

            last = -1

            for row in reader:
                try:
                    last = max(last, int(row.get("id", -1)))
                except (ValueError, TypeError):
                    continue

            next_id = last + 1

    # Write row
    write_header = not csv_file.exists() or csv_file.stat().st_size == 0

    with open(
        csv_file,
        "a" if not write_header else "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if write_header:
            writer.writeheader()

        writer.writerow({
            "id": next_id,
            "platoon_id": platoon_id,
            "total_events": total_events,
            "duration_time": duration_time,
            "testcases_id": testcases_id,
        })

    return next_id