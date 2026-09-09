#!/usr/bin/env python3
"""
Verify that paths listed in a YAML file exist relative to a given root.

Expected YAML shape (one or more top-level items, each with a numeric/string
key and a 'path' field), e.g.:

6583477:
path: Abbott,_Jane_Bingham/_/Just_for_Today

Usage:
python verify_paths.py                      # both defaults
python verify_paths.py other.yaml           # custom yaml, default root
python verify_paths.py other.yaml /my/root  # both custom

"""

import argparse
import sys
from pathlib import Path
import yaml

from utils import DATA_DIR, SCORE_DIR


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "yaml_file",
        nargs="?",
        default=DATA_DIR / "scores.yaml",
        help=f"Path to the YAML file to read (default: {DATA_DIR / 'scores.yaml'})",
    )
    ap.add_argument(
        "root",
        nargs="?",
        default=SCORE_DIR,
        help=f"Root directory that paths are relative to (default: {SCORE_DIR})",
    )
    ap.add_argument("--key", default="path", help="Field name holding the relative path (default: 'path')")
    ap.add_argument("--missing-only", default=True, action="store_true", help="Only print missing entries")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"Root directory does not exist: {root}")

    with open(args.yaml_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        sys.exit("Expected top-level YAML mapping of id -> {path: ...}")

    total = 0
    missing = 0

    for item_id, item in data.items():

        if not isinstance(item, dict) or args.key not in item:
            continue

        if not isinstance(item_id, int):
            raise ValueError(f"Invalid score key {item_id}: not an int.")
        if item_id < 0:
            raise ValueError(f"Invalid score key {item_id}: negative number.")

        total += 1
        rel_path = item[args.key]
        full_path = root / rel_path

        exists = full_path.exists()
        if not exists:
            missing += 1
            print(f"MISSING  {item_id}: {rel_path}")
        elif not args.missing_only:
            print(f"OK       {item_id}: {rel_path}")

    print(f"\n{total - missing}/{total} paths found, {missing} missing.")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
