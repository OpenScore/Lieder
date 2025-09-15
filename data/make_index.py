# -*- coding: utf-8 -*-
"""
Make index README files as contents page for the corpus.
"""
from __future__ import annotations

import markdown

from utils import get_info
from pathlib import Path

__author__ = "Mark Gotham"


# ------------------------------------------------------------------------------

def make_contents():
    """
    Produce a tabular summary of files committed to the corpus with raw
    file links to enable direct download. This is the 'README.md'.
    """
    THIS_DIR = Path(__file__).parent
    with open(THIS_DIR / "README.md", "w") as md_f:
        md_f.write("## Corpus contents with landing page for direct download\n")
        heads = ["composer", "collection", "movement", "page link"]
        md_f.write(f"|{'|'.join(heads)}|\n")
        md_f.write(f"|{'|'.join(['---'] * len(heads))}|\n")

        data = get_info("scores")
        for id in data:
            entry = data[id]
            relative_path = entry["path"]
            composer, collection, movement = [info.replace("_", " ") for info in relative_path.split("/")]
            line = [
                composer, collection, movement,
                f"[click here](https://fourscoreandmore.org/openscore/lieder/{relative_path}/)"
            ]

            md_f.write(f"|{'|'.join(line)}|\n")

    with open(THIS_DIR / "README.html", "w") as html_f:
        with open(THIS_DIR / "README.md", "r") as md_f:
            contents = md_f.read()
        contents = markdown.markdown(
            contents, extensions=["markdown.extensions.tables"]
        )
        contents = "<body>\n" + contents.replace(
            "<table>\n", '<table id="README" class="display">'
        )
        contents += '<link rel="stylesheet" href="https://cdn.datatables.net/2.1.7/css/dataTables.dataTables.css"/>\n'
        contents += '<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>\n'
        contents += '<script src="https://cdn.datatables.net/2.1.7/js/dataTables.js"></script>\n'
        contents += '<script src="search.js"></script>\n'
        contents += '</body>\n'
        html_f.write(contents)


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    make_contents()
