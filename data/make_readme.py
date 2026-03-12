# -*- coding: utf-8 -*-
"""
Make README Files (make_readme.py)
Basic script for creating the README files in every directory.

"""
from __future__ import annotations
from pathlib import Path
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


# ------------------------------------------------------------------------------

def songs(four_score: bool = False):
    yaml_data = get_info("scores")

    for this_key in yaml_data:
        print(this_key)

        entry = yaml_data[this_key]
        try:
            relative_path = entry["path"]
            name = entry["name"]
            link = entry["link"]
            imslp = entry["imslp"]

        except KeyError as e:
            print(entry)
            return f"Error: Missing key in YAML data: {e}"

        if four_score:
            destination_dir = fourscore_local / relative_path
            if not Path.exists(destination_dir):
                Path.mkdir(destination_dir)
            destination = destination_dir / "index.md"  # GitHub.io as website
        else:
            destination = path_to_scores / relative_path / "README.md"  # GitHub as repo

        with open(destination, "w") as f:

            if four_score:
                f.write("---\nlayout: post\n")
                f.write(f"title: '{name} (OpenScore Lieder Corpus)'\n---\n\n")
            else:
                f.write(f"\n# {name}\n\n")

            composer, set_name, title = relative_path.split("/")
            number = title.split("_")[0]
            try:
                number = int(number)
            except:  # known cases like "1a"
                print(f"Warning: Not a standalone and no direct str-int conversion of {number}")

            if four_score:
                set_url = four_score_public + f"{composer}/{set_name}/"
            else:
                set_url = ".."

            if four_score:
                composer_url = four_score_public + composer
                set_url = "/".join([composer_url, set_name])  # "
            else:
                composer_url = "../.."

            f.write(f"## About This Song\n\n"
                    f"- Composed by: [{composer}]({composer_url})\n"
                    )
            if set_name == "_":
                f.write(f"- A [standalone piece]({set_url})\n")
            else:
                f.write(f"- Number {number} from [{set_name.replace('_', ' ')}]({set_url})\n")

            f.write(
                f"- Transcribed and maintained by contributors to [OpenScore Lieder].\n\n"
                f"[OpenScore Lieder]: {open_score_on_muse_score}\n\n"
            )

            if four_score:  # Direct Download block
                f.write("## Direct Download\n\n"
                        "Click on the links below to download the score in your preferred format:\n"
                        "- [MuseScore (compressed)]"
                        f"({open_score_download + relative_path}/lc{this_key}.mscz?raw=true).\n"
                        f"- [MusicXML (compressed)]"
                        f"({open_score_download + relative_path}/lc{this_key}.mxl?raw=true). "
                        f"Use this version to open the file in other notation apps.\n\n")

            f.write("## External links\n\n")
            f.write(f"- MuseScore.com: view and listen to [this score][MuseScore], or download in a variety of formats.\n")
            f.write(f"- IMSLP.org: view the [source PDF file(s)][IMSLP] that this score was transcribed from.\n\n")

            f.write(f"[MuseScore]: https://musescore.com/score/{this_key}\n")
            f.write(f"[IMSLP]: https://imslp.org/wiki/Special:ReverseLookup/{imslp[1:]}\n\n")

            if four_score:
                f.write("## Preview\n\n")
                f.write(f'<iframe width="100%" height="394" src="')
                f.write(link)
                f.write('/embed" frameborder="0" allowfullscreen allow="autoplay; fullscreen"></iframe>\n')

    return None


def sets(four_score: bool = False):
    yaml_data = get_info("sets")

    for this_key in yaml_data:
        print(this_key)

        entry = yaml_data[this_key]
        try:
            relative_path = entry["path"]
            name = entry["name"]
            link = entry["link"]
            imslp = entry["imslp"]

        except KeyError:
            return f"Error: Missing key in YAML data for {this_key}"

        if four_score:
            destination_dir = fourscore_local / relative_path
            if not Path.exists(destination_dir):
                Path.mkdir(destination_dir)
            destination = destination_dir / "index.md"  # GitHub.io as website
        else:
            destination = path_to_scores / relative_path / "README.md"  # GitHub as repo

        with open(destination, "w") as f:

            if four_score:
                f.write("---\nlayout: post\n")
                f.write(f"title: '{name} (OpenScore Lieder Corpus)'\n---\n\n")
            else:
                f.write(f"\n# [{name}](..)\n\n")

            f.write(
                "## External links\n\n"
                "- MuseScore.com: View [this set] as part of the [OpenScore Lieder] collection on MuseScore.com.\n"
            )
            if imslp is not None:
                f.write(
                    f"- IMSLP.org: view the [source PDF file(s)][IMSLP] that this score was transcribed from.\n\n"
                    f"[IMSLP]: https://imslp.org/wiki/Special:ReverseLookup/{imslp[1:]}\n"
                )
            f.write(
                f"[this set]: {link}\n"
                f"[OpenScore Lieder]: {open_score_on_muse_score}\n"
            )

    return None


def composers(four_score: bool = False):
    yaml_data = get_info("composers")

    for this_key in yaml_data:
        print(this_key)

        entry = yaml_data[this_key]
        try:
            relative_path = entry["path"]
            name = entry["name"]
            desc = entry["desc"]
            born = entry["born"]
            died = entry["died"]
            link = entry["link"]

        except KeyError:
            return f"Error: Missing key in YAML data for {this_key}"

        if four_score:
            destination_dir = fourscore_local / relative_path
            if not Path.exists(destination_dir):
                Path.mkdir(destination_dir)
            destination = destination_dir / "index.md"  # GitHub.io as website
        else:
            destination = path_to_scores / relative_path / "README.md"  # GitHub as repo

        with open(destination, "w") as f:

            if four_score:
                f.write("---\nlayout: post\n")
                f.write(f"title: '{name} (OpenScore Lieder Corpus)'\n---\n\n")
            else:
                f.write(f"\n# {name}\n\n")

            f.write(f"## About {name}\n\n"
                    f"- {desc}\n"
                    f"- Dates: {born}–{died}\n\n")

            f.write("## External links\n\n"
                    "- MuseScore.com: View [sets by this composer] in [OpenScore Lieder] on MuseScore.com.\n"
                    "- Wikipedia: Crowd-sourced text about this composer on [Wikipedia].\n"
                    "- Wikidata: Crowd-sourced, structured, linked data about this composer on [Wikidata].\n\n")
            f.write(f'[Wikipedia]: {entry["wikipedia"]}\n'
                    f'[Wikidata]: https://www.wikidata.org/wiki/{entry["wikidata"]}\n'
                    f'[sets by this composer]: {link}\n'
                    f'[OpenScore Lieder]: {open_score_on_muse_score}\n\n'
                    )

    return None


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    songs(four_score=True)
    sets(four_score=True)
    composers(four_score=True)
