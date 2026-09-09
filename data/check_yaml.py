#!/usr/bin/env python3
"""
Clean up the scores.yaml file to remove redundant information.

For each entry:

Derive the expected `link` from the id
`https://musescore.com/openscore-lieder-corpus/scores/{id}`
and
derive the expected `name` from the last path segment.

This latter is more complex.
First, replace underscores in the path with spaces in the name (easy enough).
Then consider other variants.
Remove redundancy if clear; retain if (possible) ambiguity:
Examples include:
i. `04` and other leading zeros - used when there are 10+ total.
Retain `04` in path string and `4` in number.
ii. `4a`: retain as string in both.
ii. Special characters like `:` (as in `Hob.XXVIa:31`) and `?`.
This is a lossy transformation: the original cannot be be deduced from the path,
(unclear whether the original had `:`, `-`, ` `, or ``).
iii. Trailing ellipses.

If both derived values match the stored ones
then they're redundant / reconstructable,
so `name` and `link` are removed from the entry
and the file is rewritten.

If either doesn't match, the entry is left untouched and a diff is
printed for manual review.

Additionally, any `liedernet` field whose value starts with
`utils.LIEDERNET_BASE` is rewritten with
just the specific part ("suffix"), omitting that base URL.

Usage:
    python check_yaml.py scores.yaml [-o output.yaml]

If -o is omitted, the input file is overwritten in place
(a .bak backup is written first).
"""
import argparse
import sys
from pathlib import Path

import yaml

from utils import derive_number_and_name, derive_link, LIEDERNET_BASE


def process(data: dict):
    mismatches = []  # list of (id, field, expected, actual)
    cleaned = 0
    liedernet_fixed = 0
    skipped = 0

    for item_id, entry in data.items():
        if not isinstance(entry, dict):
            continue

        liedernet_link = entry.get("liedernet")
        if isinstance(liedernet_link, str) and liedernet_link.startswith(LIEDERNET_BASE):
            entry["liedernet"] = liedernet_link[len(LIEDERNET_BASE):]
            liedernet_fixed += 1

        # name / link check ---
        path = entry.get("path")
        name = entry.get("name")
        link = entry.get("link")

        if path is None or name is None or link is None:
            # Nothing to check/clean for this entry on this front.
            skipped += 1
            continue

        expected_number, expected_name = derive_number_and_name(path)
        expected_link = derive_link(item_id)

        name_ok = name == expected_name
        link_ok = link == expected_link

        number_ok = True
        if expected_number is not None:
            actual_number = entry.get("number")
            actual_str = None if actual_number is None else str(actual_number)
            if actual_str != expected_number:
                # Leading-zero difference only (e.g., "04" vs "4") not a mismatch
                simple_padding = (
                    actual_str is not None
                    and expected_number.isdigit()
                    and actual_str.isdigit()
                    and int(expected_number) == int(actual_str)
                )
                if not simple_padding:
                    number_ok = False

        if name_ok and link_ok and number_ok:
            del entry["name"]
            del entry["link"]
            cleaned += 1
        else:
            if not name_ok:
                mismatches.append((item_id, "name", expected_name, name))
            if not link_ok:
                mismatches.append((item_id, "link", expected_link, link))
            if not number_ok:
                mismatches.append(
                    (item_id, "number", expected_number, entry.get("number"))
                )

    return mismatches, cleaned, liedernet_fixed, skipped


def print_mismatches(mismatches):
    if not mismatches:
        return
    print(f"\n{len(mismatches)} mismatch(es) found:\n", file=sys.stderr)
    for item_id, field, expected, actual in mismatches:
        print(f"[{item_id}] {field} mismatch:", file=sys.stderr)
        print(f"  expected: {expected!r}", file=sys.stderr)
        print(f"  actual:   {actual!r}", file=sys.stderr)
        print(file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Clean up scores.yaml by removing redundant name/link "
        "fields and normalizing liedernet fields.",
    )
    parser.add_argument("input", help="Path to input YAML file")
    parser.add_argument(
        "-o", "--output",
        help="Path to write output YAML (default: overwrite input, with .bak backup)",
    )
    args = parser.parse_args()

    in_path = Path(args.input)

    try:
        raw_text = in_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error reading {in_path}: {exc}", file=sys.stderr)
        sys.exit(2)

    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML in {in_path}: {exc}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(data, dict):
        print(
            f"Error: expected top-level YAML mapping in {in_path}, "
            f"got {type(data).__name__}",
            file=sys.stderr,
        )
        sys.exit(2)

    mismatches, cleaned, liedernet_fixed, skipped = process(data)

    out_path = Path(args.output) if args.output else in_path
    if not args.output:
        backup = in_path.with_suffix(in_path.suffix + ".bak")
        backup.write_text(raw_text, encoding="utf-8")
        print(f"Backup written to {backup}")

    out_path.write_text(
        yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )

    print(f"Cleaned (name/link removed): {cleaned}")
    print(f"liedernet fixed: {liedernet_fixed}")
    print(f"Skipped (missing path/name/link): {skipped}")
    print(f"Wrote: {out_path}")

    print_mismatches(mismatches)
    if mismatches:
        sys.exit(1)


if __name__ == "__main__":
    main()
