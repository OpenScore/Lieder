# -*- coding: utf-8 -*-
"""
Make README Files (make_readme.py)
Basic script for creating the README files in every directory.

"""
from __future__ import annotations
from pathlib import Path
from typing import Callable
from utils import *


__author__ = "Mark Gotham"


# ------------------------------------------------------------------------------

# Local (replace with yours)
fourscore_local = path_to_data_dir.parent.parent / "fourscoreandmore.org/openscore/lieder"

# Online
four_score_public = "https://fourscoreandmore.org/openscore/lieder/"
open_score_on_muse_score = "https://musescore.com/openscore-lieder-corpus"


def base_path_to_direct_download(org: str, repo: str, branch: str = "main"):
    """
    Basic script to create the start of URLs for direct download links.
    Simply to show the structure and maintain consistency across repos.
    """
    # Ossia: return f"https://github.com/{org}/{repo}/raw/refs/heads/{branch}/"
    return f"https://github.com/{org}/{repo}/blob/{branch}/"


open_score_download = base_path_to_direct_download("openscore", "lieder", "main")
open_score_download += "scores/"


# ---------------------------------------------------------------------------
# Shared scaffolding

def _write_entries(
    what: str,
    content_writer: Callable[[str, dict, bool], str],
    four_score: bool = False,
) -> None:
    """Fetch all records for *what*, resolve each destination path, and write.

    Args:
        what:           One of "composers", "sets", "scores".
        content_writer: Callable(key, entry, four_score) → markdown string.
        four_score:     Write for the FourScore website rather than the repo.
    """
    records = get_info(what)  # list[dict] from SQLite

    for entry in records:
        key           = entry["id"]
        relative_path = entry["path"]

        print(key)

        if four_score:
            destination_dir = fourscore_local / relative_path
            destination_dir.mkdir(parents=True, exist_ok=True)
            destination = destination_dir / "index.md"
        else:
            destination = path_to_scores / relative_path / "README.md"

        with open(destination, "w") as f:
            f.write(content_writer(key, entry, four_score))


def _front_matter(name: str, four_score: bool) -> str:
    """Return the opening lines of each file (YAML front-matter or plain H1)."""
    if four_score:
        return f"---\nlayout: post\ntitle: '{name} (OpenScore Lieder Corpus)'\n---\n\n"
    return ""  # repo READMEs get their H1 from the content writers below


# ---------------------------------------------------------------------------
# Content writers  (one per entity type)

def _song_content(key: str, entry: dict, four_score: bool) -> str:
    try:
        relative_path = entry["musescore_id"]
        name          = entry["name"]
        link          = entry["link"]
        imslp         = entry["imslp"]
    except KeyError as exc:
        raise KeyError(f"Missing key in scores data for {key}: {exc}") from exc

    composer, set_name, title = relative_path.split("/")
    number = title.split("_")[0]
    try:
        number = int(number)
    except ValueError:
        print(f"Warning: not a standalone int for song number: {number!r}")

    if four_score:
        composer_url = four_score_public + composer
        set_url      = "/".join([composer_url, set_name])
    else:
        composer_url = "../.."
        set_url      = ".."

    lines = [_front_matter(name, four_score)]

    if not four_score:
        lines.append(f"# {name}\n\n")

    lines.append(
        f"## About This Song\n\n"
        f"- Composed by: [{composer}]({composer_url})\n"
    )
    if set_name == "_":
        lines.append(f"- A [standalone piece]({set_url})\n")
    else:
        lines.append(f"- Number {number} from [{set_name.replace('_', ' ')}]({set_url})\n")

    lines.append(
        f"- Transcribed and maintained by contributors to [OpenScore Lieder].\n\n"
        f"[OpenScore Lieder]: {open_score_on_muse_score}\n\n"
    )

    if four_score:
        lines.append(
            "## Direct Download\n\n"
            "Click on the links below to download the score in your preferred format:\n"
            f"- [MuseScore (compressed)]"
            f"({open_score_download + relative_path}/lc{key}.mscz?raw=true).\n"
            f"- [MusicXML (compressed)]"
            f"({open_score_download + relative_path}/lc{key}.mxl?raw=true). "
            "Use this version to open the file in other notation apps.\n\n"
        )

    lines.append(
        "## External links\n\n"
        "- MuseScore.com: view and listen to [this score][MuseScore],"
        " or download in a variety of formats.\n"
        "- IMSLP.org: view the [source PDF file(s)][IMSLP]"
        " that this score was transcribed from.\n\n"
        f"[MuseScore]: https://musescore.com/score/{key}\n"
        f"[IMSLP]: https://imslp.org/wiki/Special:ReverseLookup/{imslp[1:]}\n\n"
    )

    if four_score:
        lines.append(
            "## Preview\n\n"
            f'<iframe width="100%" height="394" src="{link}/embed"'
            ' frameborder="0" allowfullscreen'
            ' allow="autoplay; fullscreen"></iframe>\n'
        )

    return "".join(lines)


def _set_content(key: str, entry: dict, four_score: bool) -> str:
    try:
        name  = entry["name"]
        link  = entry["link"]
        imslp = entry["imslp"]
    except KeyError as exc:
        raise KeyError(f"Missing key in sets data for {key}: {exc}") from exc

    lines = [_front_matter(name, four_score)]

    if not four_score:
        lines.append(f"# [{name}](..)\n\n")

    lines.append(
        "## External links\n\n"
        "- MuseScore.com: View [this set] as part of the"
        " [OpenScore Lieder] collection on MuseScore.com.\n"
    )
    if imslp is not None:
        lines.append(
            "- IMSLP.org: view the [source PDF file(s)][IMSLP]"
            " that this score was transcribed from.\n\n"
            f"[IMSLP]: https://imslp.org/wiki/Special:ReverseLookup/{imslp[1:]}\n"
        )

    lines.append(
        f"[this set]: {link}\n"
        f"[OpenScore Lieder]: {open_score_on_muse_score}\n"
    )

    return "".join(lines)


def _composer_content(key: str, entry: dict, four_score: bool) -> str:
    try:
        name = entry["name"]
        desc = entry["desc"]
        born = entry["born"]
        died = entry["died"]
        link = entry["link"]
    except KeyError as exc:
        raise KeyError(f"Missing key in composers data for {key}: {exc}") from exc

    lines = [
        _front_matter(name, four_score),
        f"# {name}\n\n" if not four_score else "",
        f"## About {name}\n\n"
        f"- {desc}\n"
        f"- Dates: {born}–{died}\n\n",
        "## External links\n\n"
        "- MuseScore.com: View [sets by this composer] in [OpenScore Lieder]"
        " on MuseScore.com.\n"
        "- Wikipedia: Crowd-sourced text about this composer on [Wikipedia].\n"
        "- Wikidata: Crowd-sourced, structured, linked data about this"
        " composer on [Wikidata].\n\n"
        f"[Wikipedia]: {entry['wikipedia']}\n"
        f"[Wikidata]: https://www.wikidata.org/wiki/{entry['wikidata']}\n"
        f"[sets by this composer]: {link}\n"
        f"[OpenScore Lieder]: {open_score_on_muse_score}\n\n",
    ]

    return "".join(lines)


# ---------------------------------------------------------------------------

def songs(four_score: bool = False) -> None:
    _write_entries("scores", _song_content, four_score)


def sets(four_score: bool = False) -> None:
    _write_entries("sets", _set_content, four_score)


def composers(four_score: bool = False) -> None:
    _write_entries("composers", _composer_content, four_score)


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    songs(four_score=True)
    sets(four_score=True)
    composers(four_score=True)
