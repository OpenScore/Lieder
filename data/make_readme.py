# -*- coding: utf-8 -*-
"""
Make Readme Files (make_readme.py)
Basic script for creating the read me files in every directory.

"""
from __future__ import annotations
from utils import *
from urllib.parse import quote


__author__ = "Mark Gotham"


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
            set_id = entry["set_id"]
            # lyricist_url = entry["lyricist_url"]  # TODO

        except KeyError as e:
            print(entry)
            return f"Error: Missing key in YAML data: {e}"

        if four_score:
            markdown_content = "---\nlayout: post\n"
            markdown_content += f"title: '{name} (OpenScore Lieder Corpus)'\n---\n\n"
        else:
            markdown_content = "\n"
            markdown_content += f"# {name}\n\n"

        composer, set_name, title = relative_path.split("/")

        if four_score:
            set_url = four_score_and_more + quote(f"{composer}/{set_name}/")
        else:
            set_url = ".."

        if set_name == "_":
            markdown_content += f"__A [standalone piece]({set_url})"
        else:
            number = title.split("_")[0]
            try:
                number = int(number)
            except:  # known cases like "1a"
                print(f"Warning: Not a standalone and no direct str-int conversion of {number}")

            markdown_content += f"__No.{number} from [{set_name.replace("_", " ")}]({set_url})"

        if four_score:
            composer_url = four_score_and_more + quote(composer)
        else:
            composer_url = "../.."

        markdown_content += f" by [{composer}]({composer_url})__\n\n"

        markdown_content += "Transcribed and maintained by contributors to [OpenScore Lieder].\n\n"
        markdown_content += f"Please visit the [official score page] for more information.\n\n"
        markdown_content += f"[official score page]: {link}\n"
        markdown_content += f"[OpenScore Lieder]: {open_score_on_muse_score}\n\n"

        if four_score:
            markdown_content += "## Direct Download\n\n"
            markdown_content += "Click on the links below to download the score in your preferred format:\n"
            markdown_content += "- [MuseScore 4 (compressed)]"
            markdown_content += f"({four_score_and_more + quote(relative_path)}.mscz).\n"
            markdown_content += "- [MusicXML (compressed)]"
            markdown_content += f"({four_score_and_more + quote(relative_path)}.mxl). "
            markdown_content += "Use this version to open the file in other notation apps.\n"
            markdown_content += "- [MuseScore 3 (uncompressed)]"
            markdown_content += f"({raw_git + quote(relative_path)}/lc{this_key}.mscx). "
            markdown_content += "This is the version as transcribed by our team (with no updates etc.). "
            markdown_content += "It is uncompressed (so a larger file).\n\n"

        markdown_content += "## External links\n\n"
        markdown_content += f"- [MuseScore] - view and listen to [this score][MuseScore], or download in a variety of formats.\n"
        markdown_content += f"- [IMSLP] - view the [source PDF file(s)][IMSLP] that this score was transcribed from.\n\n"
        markdown_content += f"[MuseScore]: https://musescore.com/score/{this_key}\n"
        markdown_content += f"[IMSLP]: https://imslp.org/wiki/Special:ReverseLookup/{imslp[1:]}\n\n"

        if four_score:
            markdown_content += "## Preview\n\n"
            markdown_content += f'<iframe width="100%" height="394" src="'
            markdown_content += link
            markdown_content += '/embed" frameborder="0" allowfullscreen allow="autoplay; fullscreen"></iframe>\n'

        if four_score:
            destination = path_to_scores / relative_path / "index.md"  # GitHub.io as website
        else:
            destination = path_to_scores / relative_path / "README.md"  # GitHub as repo

        with open(destination, "w") as f:
            f.write(markdown_content)

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

        except KeyError as e:
            return f"Error: Missing key in YAML data for {this_key}"

        if four_score:
            markdown_content = "---\nlayout: post\n"
            markdown_content += f"title: '{name} (OpenScore Lieder Corpus)'\n---\n\n"
        else:
            markdown_content = "\n"
            markdown_content += f"# [{name}](..)\n\n"

        markdown_content += "Visit the [official set page] in [OpenScore Lieder].\n\n"
        markdown_content += f"[official set page]: {link}\n"

        # TODO: consider this nearer match to scores:
        # markdown_content += "View [sets by this composer] in [OpenScore Lieder].\n\n"
        # markdown_content += f"[sets by this composer]: {link}\n"

        markdown_content += f"[OpenScore Lieder]: {open_score_on_muse_score}\n\n"

        if four_score:
            destination = path_to_scores / relative_path / "index.md"  # GitHub.io as website
        else:
            destination = path_to_scores / relative_path / "README.md"  # GitHub as repo

        with open(destination, "w") as f:
            f.write(markdown_content)

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

        except KeyError as e:
            return f"Error: Missing key in YAML data for {this_key}"

        if four_score:
            markdown_content = "---\nlayout: post\n"
            markdown_content += f"title: '{name} (OpenScore Lieder Corpus)'\n---\n\n"
        else:
            markdown_content = "\n"
            markdown_content += f"# {name}\n\n"

        markdown_content += f"__{desc} ({born}–{died})__\n\n"
        markdown_content += "View [sets by this composer] in [OpenScore Lieder].\n\n"
        markdown_content += f"[sets by this composer]: {link}\n"
        markdown_content += f"[OpenScore Lieder]: {open_score_on_muse_score}\n\n"
        markdown_content += "## External links\n\n"
        markdown_content += "- [Wikipedia] - learn about this composer.\n"
        markdown_content += "- [Wikidata] - get data about this composer.\n\n"
        markdown_content += f'[Wikipedia]: {entry["wikipedia"]}\n'
        markdown_content += f'[Wikidata]: https://www.wikidata.org/wiki/{entry["wikidata"]}\n'

        if four_score:
            destination = path_to_scores / relative_path / "index.md"  # GitHub.io as website
        else:
            destination = path_to_scores / relative_path / "README.md"  # GitHub as repo

        with open(destination, "w") as f:
            f.write(markdown_content)

    return None


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    songs(four_score=True)
    sets(four_score=True)
    composers(four_score=False)
