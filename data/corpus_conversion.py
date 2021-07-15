# -*- coding: utf-8 -*-
"""
===============================
Corpus Conversion (corpus_conversion.py)
===============================

Mark Gotham, 2021


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Basic script for updating the `corpus_conversion.json` file with 
the latest contents of the corpus so that it can be used 
for batch conversion of all scores (mscx files) to mxl.

Implement the batch conversion with the current 
`corpus_conversion.json` from this folder with the command:
>>> mscore -j corpus_conversion.json

To create a new / updated version of the `corpus_conversion.json` file
using this script, run
>>> python3 corpus_conversion.py

This makes or updates the .json file with paired paths in this format:
    {
    "in": "../scores/<Composer>/<Set>/<Song>/<lc*>.mscx",
    "out": "../scores/<Composer>/<Set>/<Song>/<lc*>.mxl"
    }

For conversion to another file format, before the relevant step/s above,
replace '.mxl' with the desired format ('.pdf' or '.mid') either
directly in the `corpus_conversion.json` file or
in this script (the `out_format` in the prep_conversion_doc function).

For more information, and for a within-app plugin alternative, see
https://musescore.org/en/handbook/3/command-line-options#Run_a_batch_job_converting_multiple_documents

"""

import os
import json
import yaml


def get_info(what: str = 'scores'):
    """
    Retrieves the relevant corpus information: from `scores.yaml` by default.
    """

    path_to_data = os.path.join('.', what + '.yaml')

    with open(path_to_data) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    return data


def prep_conversion_doc(songs_data,
                        write: bool = False,
                        out_format: str = '.mxl'):
    """
    Prepares a list of dicts with in / out paths of proposed conversions.
    Optionally writes to a `corpus_conversion.json` file in this folder.
    """

    if out_format not in ['.mxl', '.pdf', '.mid']:
        raise ValueError('Invalid out_format')

    out_data = []
    for lc_key in songs_data:
        basic_path = os.path.join('..', 'scores', songs_data[lc_key]['path'], f'lc{lc_key}')
        x = {'in': basic_path + '.mscx',
             'out': basic_path + out_format}
        out_data.append(x)

    if write:
        out_path = os.path.join('.', 'corpus_conversion.json')
        with open(out_path, 'w') as json_file:
            json.dump(out_data, json_file)    


def run_process():
    i = get_info()
    prep_conversion_doc(i, write=True)


if __name__ == '__main__':
    run_process()
