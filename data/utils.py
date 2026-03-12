# -*- coding: utf-8 -*-
"""
Shared paths and functions
"""
from __future__ import annotations
from pathlib import Path
import sqlite3


__author__ = "Mark Gotham"


# ------------------------------------------------------------------------------

module_path = Path(__file__)
path_to_data_dir = module_path.parent
path_to_scores = path_to_data_dir.parent / "scores"
four_score_and_more = "https://fourscoreandmore.org/openscore/lieder/"
raw_git = "https://raw.githubusercontent.com/openscore/Lieder/refs/heads/main/scores/"
open_score_on_muse_score = "https://musescore.com/openscore-lieder-corpus"


# ------------------------------------------------------------------------------

# Maps the `what` argument to its corresponding table name in the DB
TABLE_MAP = {
    "composers": "composer",
    "sets":      "set",
    "scores":    "song",
}


def get_info(
        what: str = "scores",
        path_to_data: str | Path | None = None,
        db_name: str = "lieder.db",
) -> list[dict]:
    """
    Retrieve metadata from the SQLite database (replaces previous YAML-based loader).
    Converts sqlite3.Row objects to plain dicts so callers get the same type
    they previously received from yaml.load()

    Args:
        what:         One of "composers", "sets", or "scores".
        path_to_data: Directory containing the .db file. Defaults to the
                      package-level `path_to_data_dir`. TODO move to remote (URL)
        db_name:      Filename of the SQLite database (default: "lieder.db").

    Returns:
        A list of dicts, one per row, keyed by column name — the same shape
        that yaml.load() previously returned for these files.

    Raises:
        ValueError: If `what` is not one of the three valid types.
        FileNotFoundError: If the database file cannot be found.
        Exception: If the expected table is missing from the database.
    """
    valid_data_types = list(TABLE_MAP.keys())
    if what not in valid_data_types:
        raise ValueError(f"Argument `what` invalid: must be one of {valid_data_types}")

    if path_to_data is None:
        path_to_data = path_to_data_dir
    path_to_db = Path(path_to_data) / db_name

    if not path_to_db.exists():
        raise FileNotFoundError(f"Database not found at: {path_to_db}")

    table_name = TABLE_MAP[what]

    with sqlite3.connect(path_to_db) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        if not cursor.fetchone():
            raise Exception(
                f"Table '{table_name}' does not exist in {db_name}. "
                f"Expected tables: {list(TABLE_MAP.values())}"
            )

        cursor.execute(f"SELECT * FROM {table_name}")  # nosec — table name from internal map
        rows = cursor.fetchall()

    return [dict(row) for row in rows]


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    for category in ("composers", "sets", "scores"):
        print(f"\n=== {category} ===")
        try:
            records = get_info(category)
            for record in records:
                print(record)
        except Exception as exc:
            print(f"  {exc}")