[OpenScore Lieder]
==================

[OpenScore Lieder]: https://musescore.com/openscore-lieder-corpus

Mirror of https://musescore.com/openscore-lieder-corpus

Collection of songs by 19th century composers in MuseScore format with associated data.

Scores can be downloaded individually in PDF, MIDI, MusicXML, MP3 and other formats from
their [official pages][OpenScore Lieder] on MuseScore.com. Alternatively, scores can be
converted to other formats *en masse* using MuseScore's free destop software using either
the [command line interface][MuseScore Command Line] or the [Batch Convert Plugin].

[MuseScore]: https://musescore.org/
[Batch Convert Plugin]: https://musescore.org/en/project/batch-convert
[MuseScore Command Line]: https://musescore.org/en/handbook/3/command-line-options#EXAMPLES

## Directory structure

Score and lyric files are arranged in the following directory structure:

```
<composer>/<set>/<song>
```

Directories:

- `<composer>` - composer's name in the form `Last,_First_Second...`.
- `<set>` - name of the extended work that the song belongs to, if any.
    - Standalone songs go in a set called `_` (i.e. a single underscore)
- `<song>` - name of the song, including a possible prefix.
    - Prefixes (such as 1, 2, 3a, 3b, etc.) are added to songs that have a
      defined order within the set. Prefixes are zero-padded (01, 02, ...,
      09, 10, 11, etc.) where necessary to ensure the correct sort order.

## Filenames

Score files within each song directory are named as follows

```
lc<id>.mscx
```

Filename components:

- `lc` - "Lieder Corpus"
- `<id>` - the score's unique Musescore ID
    - Corpus URL: `https://musescore.com/openscore-lieder-corpus/scores/<id>`
    - Or equivalently: `https://musescore.com/score/<id>`
- `.mscx` - the file extension for MuseScore's uncompressed score format.

## Lyric files

Lyric files follow the same naming format, with the extension `.txt`: 
i.e. `lc<id>.txt`.

These files provide the lyrics (a.k.a. poem, text) for each song separately 
to assist with cross-referencing and text-based studies.
The lyrics are as automatically extracted from each relevant part of every score.
For a typical song, this means exactly one line of text.

There are some exceptions.
For the occasional part-songs in the collection (with 2 or more vocal parts) piece,
there will be one line for each part.
In these cases, the text is often identical or nearly so
(see, for instance, `Coleridge-Taylor,_Samuel/_/Viking_Song/`).

Ossia parts complicate this somewhat: they are included if they contain
lyrics, again on a separate line (first) line (above the 'real' text).
For instance, in `Gabriel,_Virginia/_/Only/`, the text file is:
```
so I must strive to for mine for ever and aye.
1. Only a face at the window, Only a face, nothing more; Yet the look in the eyes, as they meet mine, Still comes to me o’er to and o’er Only a word, man, of greeting, Only a word that was all; Yet all day, in my heart it conechoed, Like the sound of an anman gel’s call.`
```
Here the first line comes from an extra stave for a third verse alternative part, and the second provides the main text (first verse only).
Automatic processes seeking exactly one line from each lyric files should use the lowest line.

Finally, in just one case is there are 'song' with no lyrics:
`Kralik,_Mathilde/Jugend-Lieder/00_Einleitung/`.
This is a piano introduction to a song cycle.
For consistency, we include an empty `.txt` file.

See issue #1 for known challenges.

## Unicode characters in file paths

With the exception of a few unsafe or illegal characters, names of songs,
sets and composers have been left in their original forms.

Modern filesystems should have no problems with Unicode characters in
file paths. If the paths are displayed incorrectly by `git`, try setting:

```
git config core.quotePath false
```

Users on macOS may also need to set:

```
git config core.precomposeunicode true
```

__Tip:__ Add `--global` after `config` in the above commands to make `git`
behave this way by default for all repositories on your local machine.

## License and acknowledgement

These scores are released under Creative Commons Zero (CC0). See LICENSE.txt.

We kindly ask that you credit OpenScore Lieder and provide a link to
https://musescore.com/openscore-lieder-corpus or this repository for any public-facing use of these scores.

For academic publications, please cite the report we published with DLfM in 2018:

Mark Gotham, Peter Jonas, Bruno Bower, William Bosworth, Daniel Rootham, and Leigh VanHandel. 2018. ‘Scores of Scores: An OpenScore project to encode and share sheet music.’ In Proceedings of the 5th International Conference on Digital Libraries for Musicology (DLfM’18). ACM, New York, NY, USA. https://doi.org/10.1145/3273024.3273026

## Credits and more about this corpus

These scores were transcribed by contributors to OpenScore Lieder after vocal line templates by Leigh Van Handel et al., and moderated by a professional team of proofreaders.

For more about this corpus, its motivations, how to contribute, who has contributed, and the funding that has supported this social initiative, please see https://fourscoreandmore.org/scores-of-scores/

## Summary of external links

- Scores online: https://musescore.com/openscore-lieder-corpus
- Academic report: https://doi.org/10.1145/3273024.3273026
- Motivation, explanation, credits, and more: https://fourscoreandmore.org/scores-of-scores/