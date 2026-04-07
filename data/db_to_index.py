#!/usr/bin/env python3
"""
db_to_index.py
-------------
Converts the lieder database (a `.db` SQLite file)
→ to a self-contained HTML page with a
searchable, sortable table index of all songs in the collection.

Usage:
    python db_to_index.py [--db PATH] [--out PATH]

Defaults:
    --db   lieder.db
    --out  index.html
"""

import argparse
import html
import sqlite3
from pathlib import Path


__author__ = "Mark Gotham"


# ---------------------------------------------------------------------------
# Helpers


def slugify(text: str) -> str:
    """Replace spaces with underscores for URL path segments (no percent-encoding)."""
    return text.replace(" ", "_")


def build_url(composer_sort: str, set_title: str | None, song_number: str | None, song_title: str) -> str:
    """
    Construct the fourscoreandmore.org page URL for a song.

    Pattern:  /OpenScore/<composer_sort>/<set_or_dash>/<number_title>
    Singles:  set segment is '_' (bare underscore, matching the existing convention)
    """
    base = "https://fourscoreandmore.org/OpenScore"
    composer_seg = slugify(composer_sort)

    if set_title:
        set_seg = slugify(set_title)
    else:
        set_seg = "_"

    # Prefix number if present
    if song_number:
        song_seg = slugify(f"{song_number} {song_title}")
    else:
        song_seg = slugify(song_title)

    return f"{base}/{composer_seg}/{set_seg}/{song_seg}"


def esc(value) -> str:
    """HTML-escape a value (handles None gracefully)."""
    if value is None:
        return ""
    return html.escape(str(value))


# ---------------------------------------------------------------------------
# Database query


def load_rows(db_path: Path) -> list[dict]:
    """
    Return one dict per song with all display fields resolved.
    Sorted by composer (sort name) then set title then song number/title.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            c.name_sort        AS composer_sort,
            c.name_display     AS composer_display,
            s.title            AS set_title,
            sg.number          AS song_number,
            sg.title           AS song_title,
            sg.lyricist        AS lyricist,
            sg.language        AS language,
            sg.liedernet_link  AS liedernet_link,
            sg.musescore_id    AS musescore_id,
            c.musescore_singles_id AS musescore_singles_id
        FROM song sg
        JOIN composer c ON sg.composer = c.id
        LEFT JOIN sets s ON sg.sets = s.id
        ORDER BY
            c.name_sort COLLATE NOCASE,
            COALESCE(s.title, '') COLLATE NOCASE,
            sg.number  COLLATE NOCASE,
            sg.title   COLLATE NOCASE
    """)

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# HTML generation


DATATABLES_CSS = "https://cdn.datatables.net/2.1.7/css/dataTables.dataTables.min.css"
DATATABLES_JS  = "https://cdn.datatables.net/2.1.7/js/dataTables.min.js"

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OpenScore Lieder Catalogue</title>
  <link rel="stylesheet" href="{datatables_css}">
  <style>
    /* ── Layout ── */
    body {{
      font-family: Georgia, 'Times New Roman', serif;
      font-size: 0.92rem;
      line-height: 1.5;
      margin: 2rem auto;
      max-width: 1200px;
      padding: 0 1rem;
      color: #222;
      background: #fff;
    }}
    h1 {{
      font-size: 1.6rem;
      font-weight: normal;
      margin-bottom: 0.25rem;
    }}
    p.subtitle {{
      color: #555;
      margin-top: 0;
      margin-bottom: 1.5rem;
    }}

    /* ── Table ── */
    #catalogue {{
      width: 100%;
      border-collapse: collapse;
    }}
    #catalogue thead th {{
      background: #f5f5f5;
      border-bottom: 2px solid #ccc;
      padding: 0.5rem 0.75rem;
      text-align: left;
      white-space: nowrap;
      cursor: pointer;
    }}
    #catalogue tbody tr:nth-child(even) {{
      background: #fafafa;
    }}
    #catalogue tbody td {{
      padding: 0.4rem 0.75rem;
      border-bottom: 1px solid #e8e8e8;
      vertical-align: top;
    }}
    #catalogue a {{
      color: #1a5276;
      text-decoration: none;
    }}
    #catalogue a:hover {{
      text-decoration: underline;
    }}

    /* ── DataTables overrides ── */
    .dataTables_wrapper .dataTables_filter input {{
      margin-left: 0.4rem;
      border: 1px solid #ccc;
      border-radius: 3px;
      padding: 0.25rem 0.5rem;
    }}
    .dataTables_wrapper .dataTables_info,
    .dataTables_wrapper .dataTables_filter {{
      margin-bottom: 0.75rem;
    }}
  </style>
</head>
<body>
  <h1>OpenScore Lieder Catalogue</h1>
  <p class="subtitle">
    {row_count} songs by {composer_count} composers.
    Click any column header to sort; use the search box to filter.
  </p>

  <table id="catalogue">
    <thead>
      <tr>
        <th>Composer</th>
        <th>Set</th>
        <th>Song</th>
        <th>Lyricist</th>
        <th>Language</th>
        <th>Score</th>
      </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>

  <script src="{datatables_js}"></script>
  <script>
    document.addEventListener('DOMContentLoaded', function () {{
      new DataTable('#catalogue', {{
        paging: false,
        order: [],          // preserve DB sort order on load
        columnDefs: [
          {{ orderable: false, targets: 5 }}   // "Score" link column — not sortable
        ]
      }});
    }});
  </script>
</body>
</html>
"""


def render_row(r: dict) -> str:
    url = build_url(
        r["composer_sort"],
        r["set_title"],
        r["song_number"],
        r["song_title"],
    )

    # Display: prepend number to song title if present
    if r["song_number"]:
        song_display = f"{esc(r['song_number'])} {esc(r['song_title'])}"
    else:
        song_display = esc(r["song_title"])

    set_display = esc(r["set_title"]) if r["set_title"] else "—"

    return (
        f'      <tr>'
        f'<td>{esc(r["composer_display"])}</td>'
        f'<td>{set_display}</td>'
        f'<td>{song_display}</td>'
        f'<td>{esc(r["lyricist"])}</td>'
        f'<td>{esc(r["language"])}</td>'
        f'<td><a href="{esc(url)}" target="_blank" rel="noopener">View score</a></td>'
        f'</tr>'
    )


def generate_html(rows: list[dict]) -> str:
    rendered_rows = "\n".join(render_row(r) for r in rows)
    composer_count = len({r["composer_sort"] for r in rows})
    return HTML_TEMPLATE.format(
        datatables_css=DATATABLES_CSS,
        datatables_js=DATATABLES_JS,
        row_count=len(rows),
        composer_count=composer_count,
        rows=rendered_rows,
    )


# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db",  default="lieder.db",  help="Path to the SQLite database")
    parser.add_argument("--out", default="index.html", help="Output HTML file")
    args = parser.parse_args()

    db_path  = Path(args.db)
    out_path = Path(args.out)

    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    rows = load_rows(db_path)
    html_content = generate_html(rows)
    out_path.write_text(html_content, encoding="utf-8")
    print(f"Written {len(rows)} rows → {out_path}")


if __name__ == "__main__":
    main()