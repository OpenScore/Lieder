# -*- coding: utf-8 -*-
"""
===============================
Plot (plot.py)
===============================

Mark Gotham, 2021


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Basic script for extracting summary information about the corpus.

"""

from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import yaml


# ------------------------------------------------------------------------------

# Shared

def get_info(what: str = 'composers',
             path_to_data: str = './'):
    validTypes = ['composers', 'sets', 'scores']
    if what not in validTypes:
        raise ValueError('Argument `what` invalid: must be one of validTypes')
    with open(path_to_data + what + '.yaml') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    return data


# ------------------------------------------------------------------------------

# Composers

def composer_dates(plot: bool = True,
                   also_plot_active: bool = True,
                   start: int = 1730,
                   stop: int = 1950,
                   step: int = 5,
                   write_path: str = './plots/',
                   write_name: str = 'composer_dates',
                   write_format: str = 'png',
                   ):
    """
    Get birth and death dates for all composers in the corpus and 
    (optionally, plot=True, default) 
    plot the number of corpus composers that are alive in a given year.
    
    Also optionally, (also_plot_active=True, default) 
    include a secondary plot for approximate active years by removing the 
    first 20 years of each entry.
    """

    composers = get_info()  # what='composers'

    years_alive = []
    years_active = []

    for x in composers:
        b, d = composers[x]['born'], composers[x]['died']
        if b and d:  # else ignore
            [years_alive.append(x) for x in range(b, d + 1)]
            if also_plot_active:
                [years_active.append(x) for x in range(b + 20, d + 1)]

    if also_plot_active:
        what_to_plot = [years_alive, years_active]
        plot_lab = ['Alive', 'Active (approx.)']
        y_lab = 'Number of corpus composers'
    else:
        what_to_plot = years_alive
        plot_lab = ''
        y_lab = 'Number of corpus composers alive'

    bin_values = np.arange(start=start, stop=stop, step=step)

    if plot:
        plt.figure(figsize=(10, 6))
        plt.hist(what_to_plot,
                 bins=bin_values,
                 # width=step*0.95,
                 alpha=0.5,
                 align='left',
                 label=plot_lab)
        if also_plot_active:
            plt.legend()
        plt.vlines(range(1750, 1950, 50), 0, 350, linestyles='dashed')
        if step == 1:
            plt.xlabel(f'Year', fontsize=14, family='serif')
        else:
            plt.xlabel(f'Year (bin by {step} years)', fontsize=14, family='serif')
        plt.ylabel(y_lab, fontsize=14, family='serif')
        plt.xticks(bin_values, rotation=90)
        plt.tight_layout()
        plt.savefig(f'{write_path}{write_name}.{write_format}',
                    facecolor='w', edgecolor='w', format=write_format)
    else:
        return what_to_plot


# ------------------------------------------------------------------------------

# Songs

def songs_per_composer(plot: bool = True,
                       how_many: int = 15,
                       write_path: str = './plots/',
                       write_name: str = 'composer_songs',
                       write_format: str = 'png',
                       ):
    """
    Calculates the number of songs in the corpus for the
    N (`most_common`, default = 15)
    composers in the corpus.
    Optional plots (plot = True, default).
    """

    songs = get_info(what='scores')
    composers = [songs[x]['path'].split('/')[0] for x in songs]
    print(f'Total songs: {len(composers)}')
    composer_count = Counter(composers).most_common(how_many)

    if plot:
        plt.figure(figsize=(15, 10))
        plt.barh(range(len(composer_count)),
                 [x[1] for x in composer_count],
                 tick_label=['  ' + x[0].replace('_', ' ') for x in composer_count]
                 )
        plt.xlabel(f'Number of songs in the corpus', fontsize=14, family='serif')
        plt.ylabel('Composer', fontsize=14, family='serif')
        plt.tight_layout()
        plt.savefig(f'{write_path}{write_name}.{write_format}',
                    facecolor='w', edgecolor='w', format=write_format)
    else:
        return composer_count


# ------------------------------------------------------------------------------

# Sets

def songs_per_cycle(plot: bool = True,
                    start: int = 1,
                    stop: int = 32,
                    step: int = 1,
                    write_path: str = './plots/',
                    write_name: str = 'songs_per_set',
                    write_format: str = 'png',
                    ):
    """
    Plots the number of songs in each set.
    Optional plots (plot = True, default).
    """
    songs = get_info(what='scores')
    paths = ['-'.join(songs[x]['path'].split('/')[:-1]) for x in songs]
    distinct_sets = Counter(paths).most_common()

    if plot:
        bin_values = np.arange(start=start, stop=stop, step=step)

        plt.figure(figsize=(10, 6))
        plt.hist([x[1] for x in distinct_sets],
                 bins=bin_values,
                 width=step * 0.95,
                 # alpha=0.5,
                 align='left',
                 )
        plt.xlabel('Number of songs per set', fontsize=14, family='serif')
        plt.ylabel('Frequency', fontsize=14, family='serif')
        plt.tight_layout()
        plt.savefig(f'{write_path}{write_name}.{write_format}',
                    facecolor='w', edgecolor='w', format=write_format)
    else:
        return distinct_sets


# ------------------------------------------------------------------------------

def run_all():
    composer_dates()
    songs_per_composer()
    songs_per_cycle()


if __name__ == '__main__':
    run_all()
