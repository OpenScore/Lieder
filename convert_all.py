# -*- coding: utf-8 -*-
"""
MuseScore command line conversion script.
 
Intended for the lieder corpus, but applicable more widely.

By Alex Pacha (apacha) 2023
and Mark Gotham 2025 
"""

__author__ = ["Alex Pacha", "Mark Gotham"]

import argparse
import subprocess
from pathlib import Path
from tqdm import tqdm


def convert(
    in_path: Path,
    out_path: Path,
    musescore_command: str = "Applications/MuseScore 4.app/Contents/MacOS/mscore"
):
    """
    Convert one file with MuseScore command line conversion script.
    The `in_path` and `out_path` arguments are self-explanatory.
    The `musescore_command` is the path where MuseScore 4 executable is located
    on your device (adapt as needed for your OS).
    """
    convert_command = f'"{musescore_command}" -o "{str(out_path.absolute())}" "' \
                     f'{str(in_path.absolute())}"'
    process = subprocess.run(convert_command, stderr=subprocess.PIPE, text=True, shell=True)
    if not out_path.exists():
        print("Failed to convert: " + str(in_path) + "\n" + process.stderr)


if __name__ == '__main__':
    in_format = "mscx"  # TODO consider formalising all valid formats as arg, not needed at present
    out_format = "mscz"
    parser = argparse.ArgumentParser(
        description=f'Converts a directory of {in_format} files to {out_format} using MuseScore'
    )
    parser.add_argument('-i', '--input_directory', default="scores", help='The input directory')
    parser.add_argument('-o', '--output_directory', default="scores", help='The output directory')

    args = parser.parse_args()
    input_directory = Path(args.input_directory)
    output_directory = Path(args.output_directory)

    all_input_files = list(input_directory.rglob(f"*.{in_format}"))
    for in_path in tqdm(all_input_files, desc=f"Converting {in_format} to {out_format}"):
        out_path = (output_directory / in_path.relative_to(input_directory)).with_suffix(f".{out_format}")
        if out_path.exists():
            continue
        else:
            convert(in_path, out_path)
