# -*- coding: utf-8 -*-
"""
Check Scores (check_scores.py)

Check on details of the scores.

Currently only `check_all_anacruses`. More may follow.

Intended for the lieder corpus, but applicable more widely.

By Mark Gotham 2025

To run:
`python3 check_scores.py -i "/your/path/to/openscore/lieder"`
replacing with your path.
"""

__author__ = "Mark Gotham"


from music21 import converter, stream
from pathlib import Path
from utils import path_to_scores


def check_all_anacruses(
        base_path: Path = path_to_scores,
        file_type: str = ".mxl",
) -> None:
    """
    Get all scores across a corpus (base_path).
    and check on the anacruses of every score in the given directory.

    :param base_path: THe top level of the directory to search.
    :param file_type: The file type to search for.
    """

    files = base_path.rglob("*" + file_type)
    for score_path in files:
        try:
            score = converter.parse(score_path)
        except:
            print(f"Cannot parse score {score_path}")
            continue

        try:
            ts = score.getTimeSignatures()[0]  # assuming all have one at the start.
        except:
            print(f"`getTimeSignatures` fail: cannot retrieve from {score_path}")
            continue

        first_measure = score.parts[0].getElementsByClass(stream.Measure)[0]
        # Not: first_measure = score.measures(0, 0)  # First part, first measure

        if first_measure is None:
            print(f"Cannot retrieve a first measure from {score_path}")
            continue

        nominal_duration = ts.numerator * 4 / ts.denominator  # e.g., 4/4 → 4.0, 6/8 -> 3.0
        num = first_measure.measureNumber
        actual_duration = first_measure.duration.quarterLength
        #: Not first_measure.barDuration.quarterLength

        str_base = f"Score: {score_path}, nominally {nominal_duration}, actually {actual_duration}, numbered {num}."

        if nominal_duration == actual_duration:
            if num != 1:
                print("!! Error: not anacrustic. " + str_base)
        elif actual_duration == 0:
            print("!! Error: first measure has length 0. " + str_base)
        elif actual_duration < nominal_duration:  # anacrusis
            if num == 0:
                pass  # correct
            elif num == 1:
                    print("!! Error: anacrustic but numbered 1. " + str_base)
                    continue
            else:  # not 0 or 1
                print("!! Eccentric first measure number. " + str_base)
                continue
        elif actual_duration > nominal_duration:
            print("!! Very strange overlong case. " + str_base)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check if leaf directories contain specific file formats.")

    parser.add_argument('-i', '--root_directory', default="../scores", help='The root directory')
    parser.add_argument('-f', '--format', default=".mxl", help="The file format to search for.")

    args = parser.parse_args()
    check_all_anacruses(Path(args.root_directory), args.format)
