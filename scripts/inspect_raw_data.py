"""Inspect raw retail forecasting CSV files without modifying them."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd

DATE_COLUMN_CANDIDATES = {"date", "Date"}
CHUNK_SIZE = 1_000_000
INDEX_COLUMN_NAMES = {"Unnamed: 0", ""}


def _read_header(file_path: Path) -> list[str]:
    """Read and parse the CSV header row without loading the full file."""
    with open(file_path, encoding="utf-8-sig", newline="") as file_handle:
        header_line = file_handle.readline()
    return next(csv.reader([header_line]))


def _count_physical_lines(file_path: Path, header_field_count: int) -> tuple[int, int]:
    """Return (physical data lines, ragged lines) for a CSV file.

    A ragged line is a data line whose comma count differs from the header's,
    which happens when text fields contain unquoted commas. These lines are
    skipped by the parser and are therefore reported rather than silently lost.
    """
    expected_commas = header_field_count - 1
    total = 0
    ragged = 0
    with open(file_path, encoding="utf-8-sig", newline="") as file_handle:
        next(file_handle, None)  # skip header
        for line in file_handle:
            total += 1
            if line.count(",") != expected_commas:
                ragged += 1
    return total, ragged


def profile_csv(file_path: Path) -> dict:
    """Return a structural profile for one CSV file without modifying it."""
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if file_path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a CSV file: {file_path}")

    header_columns = _read_header(file_path)

    index_column = None
    if header_columns and header_columns[0] in INDEX_COLUMN_NAMES:
        index_column = "Unnamed: 0"
    data_columns = [
        column for column in header_columns if column not in INDEX_COLUMN_NAMES
    ]

    physical_rows, ragged_lines = _count_physical_lines(
        file_path, len(header_columns)
    )

    profile = {
        "file": file_path.name,
        "size_bytes": int(file_path.stat().st_size),
        "rows": 0,
        "columns": len(data_columns),
        "column_names": data_columns,
        "dtypes": {},
        "missing_values": {},
        "duplicate_rows": 0,
        "unique_values": {},
        "index_column": index_column,
        "lines_skipped": ragged_lines,
        "physical_rows": physical_rows,
    }

    missing_counts = {column: 0 for column in header_columns}
    unique_counts: dict[str, set[str]] = {
        column: set()
        for column in data_columns
        if column in {"store_id", "item_id"}
    }
    duplicate_rows = 0
    date_column = None
    invalid_dates = 0
    date_min = None
    date_max = None
    dtypes_set = False

    for chunk in pd.read_csv(
        file_path,
        encoding="utf-8-sig",
        chunksize=CHUNK_SIZE,
        on_bad_lines="skip",
    ):
        chunk = chunk[
            [column for column in chunk.columns if column not in INDEX_COLUMN_NAMES]
        ]

        if not dtypes_set and not chunk.empty:
            profile["dtypes"] = {
                column: str(dtype) for column, dtype in chunk.dtypes.items()
            }
            dtypes_set = True

        profile["rows"] += len(chunk)
        duplicate_rows += int(chunk.duplicated().sum())

        for column in chunk.columns:
            missing_counts[column] += int(chunk[column].isna().sum())

        for column, values in unique_counts.items():
            if column in chunk.columns:
                values.update(
                    chunk[column].dropna().astype(str).str.strip().tolist()
                )

        if date_column is None:
            candidates = [
                column
                for column in chunk.columns
                if column in DATE_COLUMN_CANDIDATES
            ]
            if candidates:
                date_column = candidates[0]

        if date_column is not None and date_column in chunk.columns:
            parsed = pd.to_datetime(chunk[date_column], errors="coerce")
            invalid_dates += int(parsed.isna().sum())
            valid = parsed.dropna()
            if not valid.empty:
                chunk_min = valid.min()
                chunk_max = valid.max()
                date_min = chunk_min if date_min is None else min(date_min, chunk_min)
                date_max = chunk_max if date_max is None else max(date_max, chunk_max)

    profile["missing_values"] = {
        column: count
        for column, count in missing_counts.items()
        if count > 0
    }
    profile["duplicate_rows"] = duplicate_rows
    profile["unique_values"] = {
        column: len(values) for column, values in unique_counts.items()
    }

    if date_column is not None:
        profile["date_column"] = date_column
        profile["invalid_date_values"] = invalid_dates
        if date_min is not None:
            profile["date_min"] = date_min.date().isoformat()
            profile["date_max"] = date_max.date().isoformat()
        else:
            profile["date_min"] = None
            profile["date_max"] = None

    return profile


def inspect_directory(data_directory: Path) -> list[dict]:
    """Inspect every CSV file in a directory."""
    if not data_directory.exists():
        raise FileNotFoundError(
            f"Raw-data directory does not exist: {data_directory}"
        )

    csv_files = sorted(data_directory.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {data_directory}"
        )

    return [profile_csv(file_path) for file_path in csv_files]


def print_profile(profile: dict) -> None:
    """Print one profile in a human-readable format."""
    print("=" * 72)
    print(f"FILE: {profile['file']}")
    print(f"SIZE BYTES: {profile['size_bytes']:,}")
    print(f"ROWS (PARSED): {profile['rows']:,}")
    print(f"ROWS (PHYSICAL): {profile['physical_rows']:,}")
    print(f"LINES SKIPPED: {profile['lines_skipped']:,}")
    print(f"COLUMNS: {profile['columns']}")
    print(f"COLUMN NAMES: {', '.join(profile['column_names'])}")
    print(f"INDEX COLUMN DROPPED: {profile['index_column']}")
    print(f"DUPLICATE ROWS: {profile['duplicate_rows']:,}")

    print("DATA TYPES:")
    for column, dtype in profile["dtypes"].items():
        print(f"  - {column}: {dtype}")

    print("MISSING VALUES:")
    if profile["missing_values"]:
        for column, count in profile["missing_values"].items():
            print(f"  - {column}: {count:,}")
    else:
        print("  - None")

    print("UNIQUE IDENTIFIERS:")
    if profile["unique_values"]:
        for column, count in profile["unique_values"].items():
            print(f"  - {column}: {count:,}")
    else:
        print("  - None detected")

    if "date_column" in profile:
        print(f"DATE COLUMN: {profile['date_column']}")
        print(
            f"INVALID DATE VALUES: "
            f"{profile['invalid_date_values']:,}"
        )
        print(f"DATE MIN: {profile['date_min']}")
        print(f"DATE MAX: {profile['date_max']}")

    print()


def main() -> None:
    """Run raw-data inspection from the command line."""
    parser = argparse.ArgumentParser(
        description="Inspect raw retail forecasting CSV files."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory containing raw CSV files.",
    )

    args = parser.parse_args()

    profiles = inspect_directory(args.data_dir)

    print(f"Inspected {len(profiles)} CSV file(s).")
    print()

    for profile in profiles:
        print_profile(profile)


if __name__ == "__main__":
    main()
