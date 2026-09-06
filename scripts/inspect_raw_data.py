"""Inspect raw retail forecasting CSV files without modifying them."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

DATE_COLUMN_CANDIDATES = {"date", "Date"}


def profile_csv(file_path: Path) -> dict:
    """Return a structural profile for one CSV file."""
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if file_path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a CSV file: {file_path}")

    dataframe = pd.read_csv(file_path)

    profile = {
        "file": file_path.name,
        "rows": int(dataframe.shape[0]),
        "columns": int(dataframe.shape[1]),
        "column_names": dataframe.columns.tolist(),
        "dtypes": {
            column: str(dtype)
            for column, dtype in dataframe.dtypes.items()
        },
        "missing_values": {
            column: int(value)
            for column, value in dataframe.isna().sum().items()
            if value > 0
        },
        "duplicate_rows": int(dataframe.duplicated().sum()),
        "unique_values": {},
    }

    for column in dataframe.columns:
        if column in {"store_id", "item_id"}:
            profile["unique_values"][column] = int(
                dataframe[column].nunique(dropna=True)
            )

    date_columns = [
        column
        for column in dataframe.columns
        if column in DATE_COLUMN_CANDIDATES
    ]

    if date_columns:
        date_column = date_columns[0]
        parsed_dates = pd.to_datetime(
            dataframe[date_column],
            errors="coerce",
        )

        profile["date_column"] = date_column
        profile["invalid_date_values"] = int(parsed_dates.isna().sum())

        valid_dates = parsed_dates.dropna()

        if not valid_dates.empty:
            profile["date_min"] = valid_dates.min().date().isoformat()
            profile["date_max"] = valid_dates.max().date().isoformat()
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
    print(f"ROWS: {profile['rows']}")
    print(f"COLUMNS: {profile['columns']}")
    print(f"COLUMN NAMES: {', '.join(profile['column_names'])}")
    print(f"DUPLICATE ROWS: {profile['duplicate_rows']}")

    print("DATA TYPES:")
    for column, dtype in profile["dtypes"].items():
        print(f"  - {column}: {dtype}")

    print("MISSING VALUES:")
    if profile["missing_values"]:
        for column, count in profile["missing_values"].items():
            print(f"  - {column}: {count}")
    else:
        print("  - None")

    print("UNIQUE IDENTIFIERS:")
    if profile["unique_values"]:
        for column, count in profile["unique_values"].items():
            print(f"  - {column}: {count}")
    else:
        print("  - None detected")

    if "date_column" in profile:
        print(f"DATE COLUMN: {profile['date_column']}")
        print(
            f"INVALID DATE VALUES: "
            f"{profile['invalid_date_values']}"
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
