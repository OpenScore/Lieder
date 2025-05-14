# -*- coding: utf-8 -*-
"""
===============================
Make Readme Files (make_readme.py)
===============================

Mark Gotham, 2025


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Basic script for creating the read me files in every directory.

"""
from __future__ import annotations
from pathlib import Path
import yaml


__author__ = "Mark Gotham"


# ------------------------------------------------------------------------------

# Shared

module_path = Path(__file__)
path_to_data_dir = module_path.parent
path_to_scores = path_to_data_dir.parent / "scores"


def get_info(
        what: str = "songs",
        path_to_data: str | Path | None = None
):
    
    valid_data_types = ["composers", "sets", "scores"]
    if what not in valid_data_types:
        raise ValueError(f"Argument `what` invalid: must be one of {valid_data_types}")

    if path_to_data is None:
        path_to_data = path_to_data_dir

    path_to_data /= f"{what}.yaml"

    with open(path_to_data) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    return data


# ------------------------------------------------------------------------------

# Songs

def songs():
    yaml_data = get_info("scores")

    for this_key in yaml_data:
        print(this_key)
        markdown_content = "\n"
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

        composer, set_name, title = relative_path.replace("_", " ").split("/")
        markdown_content += f"# {name}\n\n"

        if set_name == " ":
            markdown_content += f"__A [standalone piece](..)"  # TODO check valid markdown hosting elsewhere
        else:
            number = title.split(" ")[0]
            try:
                number = int(number)
                markdown_content += f"__No.{number} from [{set_name}](..)"  # TODO as above
            except:
                markdown_content += f"__No.{number} from [{set_name}](..)"  # TODO as above

        markdown_content += f" by [{composer}](../..)__\n\n"  # TODO as above

        markdown_content += "Transcribed and maintained by contributors to [OpenScore Lieder].\n\n"
        markdown_content += f"Please visit the [official score page] for more information.\n\n"
        markdown_content += f"[official score page]: {link}\n"
        markdown_content += "[OpenScore Lieder]: https://musescore.com/openscore-lieder-corpus\n\n"
        markdown_content += "## External links\n\n"
        markdown_content += f"- [MuseScore] - view and listen to [this score][MuseScore], or download in a variety of formats.\n"
        markdown_content += f"- [IMSLP] - view the [source PDF file(s)][IMSLP] that this score was transcribed from.\n\n"
        markdown_content += f"[MuseScore]: https://musescore.com/score/{this_key}\n"
        markdown_content += f"[IMSLP]: https://imslp.org/wiki/Special:ReverseLookup/{imslp[1:]}\n"

        # destination = path_to_scores / relative_path / f"{this_key}.md"
        destination = path_to_scores / relative_path / "README.md"
        with open(destination, "w") as f:
            f.write(markdown_content)

    return None


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    songs()
