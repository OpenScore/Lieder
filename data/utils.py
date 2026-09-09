from pathlib import Path
from html import escape

RAW_BASE = "https://raw.githubusercontent.com/OpenScore/Lieder/refs/heads/main/scores/"
LINK_BASE = "https://musescore.com/openscore-lieder-corpus/scores/"
IMSLP_BASE = "https://imslp.org/wiki/Special:ReverseLookup/"
LIEDERNET_BASE = "https://www.lieder.net/lieder/"

REPO_DIR = Path(__file__).parent.parent
DATA_DIR = REPO_DIR / "data"
SCORE_DIR = REPO_DIR / "scores"


def make_link(url, label):
    safe_url = escape(url, quote=True)
    return f'<a href="{safe_url}" target="_blank" rel="noopener">{label}</a>'


def derive_link(item_id) -> str:
    return f"{LINK_BASE}{item_id}"


def derive_number_and_name(path: str) -> tuple[str, str]:
    """Derive the expected (`number`, `name`) from the last segment of `path`.

    The last segment is split on "_". If the first token starts with a
    digit (e.g. "4", "3a"), it's treated as the track number and stripped
    from the name; the remaining tokens are joined with spaces to form the
    name. If the first token doesn't start with a digit, there's no
    number and the whole segment (underscores -> spaces) is the name.

    >>> derive_number_and_name("4_Title")
    ('4', 'Title')

    >>> derive_number_and_name("04_Longer_Title")
    ('04', 'Longer Title')

    >>> derive_number_and_name("04a_Title")
    ('04a', 'Title')

    """
    last = path.rstrip("/").split("/")[-1]
    parts = last.split("_")
    number = None
    if parts and parts[0][:1].isdigit():
        number = parts[0]
        parts = parts[1:]
    name = " ".join(parts).strip()
    return number, name

if __name__ == "__main__":
    import doctest
    doctest.testmod()