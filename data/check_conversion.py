# -*- coding: utf-8 -*-
"""
Check Conversion (corpus_conversion.py)

Having run a batch convert, verify that files of the expected format are in each child directory.

Intended for the lieder corpus, but applicable more widely.

By Mark Gotham 2025

To run:
`python3 check_conversion.py -i "/your/path/to/openscore/lieder"`
replacing with your path.
"""

__author__ = "Mark Gotham"

from pathlib import Path


def check_leaf_directories_have_file_of_given_format(root_dir: Path, format: str = ".mxl"):
    """
    Checks if every leaf directory (a directory with no subdirectories)
    under the given root directory contains at least one file of the given format.

    Args:
        root_dir: The path to the root directory to check (as a Path object).
        format: The format to search for.

    Returns:
        True if all leaf directories contain at least one file of the given format, None otherwise.
        Also prints specific errors for any leaf directories that do contain at least one such file.
    """

    root_path = Path(root_dir)
    all_correct = True

    for dirpath in root_path.glob("**/*"):
        if not dirpath.is_dir():
            continue

        has_subdir = any(p.is_dir() for p in dirpath.iterdir())

        if not has_subdir:
            csv_found = False
            for filename in dirpath.iterdir():
                if filename.suffix.lower() == format:
                    csv_found = True
                    break

            if not csv_found:
                print(f"{dirpath} is a leaf directory but does not contain any {format} files.")
                all_correct = False

    return all_correct


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check if leaf directories contain specific file formats.")

    parser.add_argument('-i', '--root_directory', default="../scores", help='The root directory')
    parser.add_argument('-f', '--format', default=".mxl", help="The file format to search for.")

    args = parser.parse_args()

    if check_leaf_directories_have_file_of_given_format(args.root_directory, args.format):
        print(f"All leaf directories contain at least one {args.format} file.")
    else:
        print(f"Some leaf directories are missing {args.format} file, as printed above.")
