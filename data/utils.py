# -*- coding: utf-8 -*-
"""
Shared paths and functions

"""
from __future__ import annotations
from pathlib import Path
import yaml


__author__ = "Mark Gotham"


# ------------------------------------------------------------------------------

module_path = Path(__file__)
path_to_data_dir = module_path.parent
path_to_scores = path_to_data_dir.parent / "scores"
four_score_and_more = "https://fourscoreandmore.org/openscore/lieder/"
raw_git = "https://raw.githubusercontent.com/openscore/Lieder/refs/heads/main/scores/"
open_score_on_muse_score = "https://musescore.com/openscore-lieder-corpus"


# ------------------------------------------------------------------------------

def get_info(
        what: str = "songs",
        path_to_data: str | Path | None = None
):
    """Retrieve a YAML metadata file (one of three)."""
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
