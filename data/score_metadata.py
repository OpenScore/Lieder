# -*- coding: utf-8 -*-
"""
Retrieve useful metadata from the scores,
not the title, composer etc. (we have that already),
but the instrumentation and lyrics.
"""

from __future__ import annotations
from music21 import converter, stream, text
from pathlib import Path
import re
from utils import path_to_scores

accompaniment_parts_no_lyrics = ("Piano", "Guitar")  # Any others?

__author__ = "Mark Gotham"


# ------------------------------------------------------------------------------

def corpus_retrieve(
        base_path: Path = path_to_scores,
        file_type: str = ".mxl",
        overwrite: bool = True,
):
    """
    Get all scores across a corpus (base_path).
    extract the lyrics from the score and write the file.

    :param base_path: THe top level of the directory to search.
    :param file_type: The file type to search for.
    :param overwrite: If False and there is a corresponding lyrics file saved, skip.
    """
    files = base_path.rglob("*" + file_type)
    for score_path in files:
        text_path = score_path.with_suffix(".txt")
        if overwrite or (not Path.exists(text_path)):
            try:
                score = converter.parse(score_path)
            except:
                print(f"Cannot parse score {score_path}")
                continue

            voices = []
            for i in range(len(score.parts)):
                part = score.parts[i]
                this_instrument = part.getInstrument()

                if this_instrument is not None:
                    if any(x in accompaniment_parts_no_lyrics for x in this_instrument.classes):
                        pass
                    else:
                        voices.append(i)
                else:
                    print(f"No instrument information for part {i}")

            if len(voices) == 0:
                print(f"No voice parts in {score_path}, defaulting to the top most")
            lyrics = extract_lyrics_from_score(score, part_numbers=voices)
            with open(text_path, "w") as f:
                f.write(lyrics)


# ------------------------------------------------------------------------------

def extract_lyrics_from_score(
        score: stream.Score,
        part_numbers: list[int] | None = None,
        standardise: bool = True,
) -> str:
    """
    Extract the lyrics from a score.

    This function writes all parts among those specified that contain lyrics on separate lines.
    For a typical song with one vocal part, this is one line.
    For a chorale (e.g., SATB), there will be vocal lines and so 4 textual lines.

    Most scores are voice and piano, but there are exceptions:
    - Ossia parts may complicate this, though if there are no lyrics, then the part is not included.
    - part songs include multiple voices (e.g. SATB+piano) and
    - the accompaniment is not always voice (e.g., guitar in Zumsteeg _Sehnsucht der Liebe_).
    - in rare cases (piano introduction) there is no voice at all.

    :param score: An already parsed music21.score object.
    :param part_numbers: User may specify which part or parts to use (by number in the score order).
        By default, it is set to None, in which case all parts are processed.
    :param standardise: Perform basic standardisation of explicitly entered syllable breaks and various kind of dash.

    """
    if part_numbers is None:
        part_numbers = range(len(score.parts))

    out_string = ""
    for i in part_numbers:
        part = score.parts[i]
        lyrics = text.assembleAllLyrics(part)  # NB: all for the case of all lines
        if standardise:
            lyrics = lyrics.replace("- ", "")  # Explicitly entered syllable breaks
            lyrics = lyrics.replace("- ", "")  # Sic, another kind of dash
            # TODO systematic check: when fixing raw text files manually, decide on adjustments needed here / in score.

        if lyrics:  # still no lyrics in some vocal parts ...
            out_string += f"{lyrics}\n"
        else:  # ... placeholder when empty
            out_string += f"[No lyrics on part {i}]\n"

    return out_string


def reorder_numbered_list(text: str) -> str | None:
    """
    In many cases, the text will be retrieved in a complex order.

    Use this to
    - pattern match numbered items (1-9) followed by a period and optional whitespace,
    - find all matching cases, numbered items (1-9 only)
    - sort by those number
    """
    pattern = r'(\d+)\.\s*(.*?)(?=\s*\d+\.\s*|\Z)'
    items = []

    for match in re.finditer(pattern, text, re.DOTALL):
        num = int(match.group(1))
        if 1 <= num <= 9:
            items.append((num, match.group(2)))

    if not items:
        return None

    items.sort(key=lambda x: x[0])

    return "\n".join([f"{num}. {text_part}" for num, text_part in items])


def read_reorder_write(text_path: Path) -> None:
    with open(text_path, "r") as f:
        text = f.read()

    output_text = reorder_numbered_list(text)
    
    if output_text is not None:
        with open(text_path, "w") as f:
            f.write(output_text)


def corpus_reorder(base_path: Path = path_to_scores) -> None:
    """
    Get all text files across a corpus (base_path).
    and attempt to reorder the verses in the correct order.
    TODO not perfect, but an improvement overall.

    :param base_path: The top level of the directory to search.
    """
    files = base_path.rglob("*.txt")
    for text_path in files:
        read_reorder_write(text_path)


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    # corpus_retrieve()
    corpus_reorder()
