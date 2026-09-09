#!/usr/bin/env python3
"""
Build the OpenScore Lieder Catalogue:
a single sortable/searchable table
with columns for
Composer / Set / Song / Lyricist / Language / Score / External.

The design is lightweight, with DataTables via CDN.

This script builds that .html from the .yaml data:
composers.yaml / sets.yaml / scores.yaml.

"""
import yaml
from urllib.parse import quote

from utils import *

OUT_FILE = DATA_DIR / "index.html"


HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OpenScore Lieder Catalogue</title>
  <link rel="stylesheet" href="https://cdn.datatables.net/2.1.7/css/dataTables.dataTables.min.css">
  <style>
    /* ── Layout ── */
    body {
      font-family: Georgia, 'Times New Roman', serif;
      font-size: 0.92rem;
      line-height: 1.5;
      margin: 2rem auto;
      max-width: 1200px;
      padding: 0 1rem;
      color: #222;
      background: #fff;
    }
    h1 {
      font-size: 1.6rem;
      font-weight: normal;
      margin-bottom: 0.25rem;
    }
    p.subtitle {
      color: #555;
      margin-top: 0;
      margin-bottom: 1.5rem;
    }

    /* ── Table ── */
    #catalogue {
      width: 100%;
      border-collapse: collapse;
    }
    #catalogue thead th {
      background: #f5f5f5;
      border-bottom: 2px solid #ccc;
      padding: 0.5rem 0.75rem;
      text-align: left;
      white-space: nowrap;
      cursor: pointer;
    }
    #catalogue tbody tr:nth-child(even) {
      background: #fafafa;
    }
    #catalogue tbody td {
      padding: 0.4rem 0.75rem;
      border-bottom: 1px solid #e8e8e8;
      vertical-align: top;
    }
    #catalogue a {
      color: #1a5276;
      text-decoration: none;
    }
    #catalogue a:hover {
      text-decoration: underline;
    }

    /* ── DataTables overrides ── */
    .dataTables_wrapper .dataTables_filter input {
      margin-left: 0.4rem;
      border: 1px solid #ccc;
      border-radius: 3px;
      padding: 0.25rem 0.5rem;
    }
    .dataTables_wrapper .dataTables_info,
    .dataTables_wrapper .dataTables_filter {
      margin-bottom: 0.75rem;
    }
  </style>
</head>
<body>
  <h1>OpenScore Lieder Catalogue</h1>
  <p class="subtitle">
    __N_SONGS__ songs by __N_COMPOSERS__ composers.
    Click any column header to sort; use the search box to filter (across any field).
  </p>
  <p>
  Score files are provided in several formats:
  <ol>
      <li>MuseScore, for use in MuseScore studio (layout set out by us, manually),</li>
      <li>MusicXML, which is usable in almost any score reader (layout may be broken).</li>
  </ol>
  </p>
  <p>
  External links are provided to:
  <ol>
      <li>IMSLP.org for the source edition (PDF) on which ours is based.
      <li>MuseScore.com to view and play online
      (but note that downloads are behind a paywall, so use the score links for download)
      <li>Lieder.net to view song texts (in most but not all cases).
  </ol>           
  </p>
  <p>
  We hope you enjoy this resource!
  </p>
  <p>
  <a href="https://markgotham.github.io/" target="_blank" rel="noopener">Mark Gotham</a>,
  on behalf of the OpenScore team.
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
        <th>External</th>
      </tr>
    </thead>
    <tbody>
"""

TAIL = """    </tbody>
  </table>

  <!-- jQuery MUST load before DataTables -->
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
  <script src="https://cdn.datatables.net/2.1.7/js/dataTables.min.js"></script>
  <script>
    document.addEventListener('DOMContentLoaded', function () {
      new DataTable('#catalogue', {
        paging: false,
        order: [],          // preserve DB sort order on load
        columnDefs: [
          { orderable: false, targets: 5 }   // "Score" link column — not sortable
        ]
      });
    });
  </script>
</body>
</html>
"""


def score_files_links(path, key):
    encoded = quote(path, safe="/")
    id_part = str(key) if key > 0 else "None"
    base = f"{RAW_BASE}{encoded}/lc{id_part}"
    mscz = f'<a href="{base}.mscz?raw=true" target="_blank" rel="noopener">MuseScore</a>'
    mxl = f'<a href="{base}.mxl?raw=true" target="_blank" rel="noopener">MusicXML</a>'
    return f"{mscz}; {mxl}"


def main():
    composers = yaml.safe_load(open(DATA_DIR / "composers.yaml", encoding="utf-8")) or {}
    sets_ = yaml.safe_load(open(DATA_DIR / "sets.yaml", encoding="utf-8")) or {}
    scores = yaml.safe_load(open(DATA_DIR / "scores.yaml", encoding="utf-8")) or {}

    composer_path_to_key = {v.get("path"): k for k, v in composers.items() if v.get("path")}

    def resolve_composer_and_set(key, s):
        """Returns (composer_name, set_display_name) or (None, None) if the
        composer can't be determined at all."""
        sid = s.get("set_id")
        if sid is not None and sid in sets_:
            set_rec = sets_[sid]
            comp_key = set_rec.get("composer_id")
            comp = composers.get(comp_key)
            if comp:
                is_singles = (set_rec.get("path", "").endswith("/_"))
                return comp["name"], ("—" if is_singles else set_rec.get("name", "—"))
        # fall back to the composer segment of the score's own path
        first_seg = s.get("path", "").split("/")[0]
        comp_key = composer_path_to_key.get(first_seg)
        if comp_key is not None:
            return composers[comp_key]["name"], "—"
        return None, None

    rows = []  # (sort_path, composer, set_name, song, lyricist, language, links_html)
    for key, s in scores.items():
        if not isinstance(key, int):
            raise ValueError(f"Invalid score key {key}: not an int.")
        if key < 0:
            raise ValueError(f"Invalid score key {key}: negative number.")
        path = s.get("path")
        if not path:
            raise ValueError(f"No path for {key}")
        composer_name, set_name = resolve_composer_and_set(key, s)
        if composer_name is None:
            continue

        number, title = derive_number_and_name(path)

        name = s.get("name")
        if name:
            title = name # Overwrite, rare

        num = s.get("number")
        if num:
            number = num # Overwrite, rare

        song_display = f"{number} {title}" if number else title

        lyricist = s.get("lyricist", "") or ""
        language = (s.get("language") or "").upper()
        links_html = score_files_links(path, key)

        # Ext IMSLP and MS required, liedernet optional
        imslp_raw = s.get("imslp")
        if not imslp_raw:  # Sic, required in all cases
            raise ValueError(f"No imslp id for {key}")

        imslp_url = f"{IMSLP_BASE}{quote(imslp_raw[1:])}"  # strip leading '#'
        links = [
            (imslp_url, "IMSLP.org"),
            (f"{LINK_BASE}{quote(str(key))}", "MuseScore.com"),
        ]
        if liedernet := s.get("liedernet"):
            links.append((f"{LIEDERNET_BASE}{quote(str(liedernet))}", "Lieder.net"))

        external = "; ".join(make_link(u, l) for u, l in links)

        rows.append((path, composer_name, set_name, song_display, lyricist, language, links_html, external))

    rows.sort(key=lambda r: r[0])

    n_songs = len(rows)
    n_composers = len({r[1] for r in rows})

    body_lines = []
    for _, composer, set_name, song, lyricist, language, links_html, external in rows:
        body_lines.append(
            "      <tr>"
            f"<td>{escape(composer)}</td>"
            f"<td>{escape(set_name)}</td>"
            f"<td>{escape(song)}</td>"
            f"<td>{escape(lyricist)}</td>"
            f"<td>{escape(language)}</td>"
            f"<td>{links_html}</td>"
            f"<td>{external}</td>"
            "</tr>\n"
        )

    html = (HEAD.replace("__N_SONGS__", str(n_songs)).replace("__N_COMPOSERS__", str(n_composers))
            + "".join(body_lines) + TAIL)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Wrote {OUT_FILE}: {n_songs} songs, {n_composers} composers.")


if __name__ == "__main__":
    main()
