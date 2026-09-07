#!/usr/bin/env python3
"""
check_wikidata.py

load the composers.yaml file,
validate all URLs,
and verify Wikidata QIDs - flagging possible errors to review.

"""

import yaml
import requests
from difflib import SequenceMatcher
from urllib.parse import urlparse

API = "https://www.wikidata.org/w/api.php"
HEADERS = {
    "User-Agent": "OpenScore/1.0 (https://musescore.com/openscore-string-quartets; no@email.com)"
}

# Fields expected to hold a full URL (when present)
URL_FIELDS = {"link", "wikipedia", "imslp", "image"}


def is_valid_url(value: str) -> bool:
    try:
        r = urlparse(value)
        return r.scheme in ("http", "https") and bool(r.netloc)
    except (ValueError, AttributeError):
        return False


def get_wikidata_labels(qids: list[str], languages: str | None = "en") -> dict[str, str]:
    """Fetch labels for a batch of QIDs. If languages is None, return first available."""
    params = {
        "action": "wbgetentities",
        "ids": "|".join(qids),
        "props": "labels",
        "format": "json",
    }
    if languages:
        params["languages"] = languages

    r = requests.get(API, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    out = {}
    for qid, entity in data.get("entities", {}).items():
        labels = entity.get("labels", {})
        if languages:
            label = labels.get(languages, {}).get("value", "")
            out[qid] = label
        else:
            # pick first non-empty label in any language
            for lab in labels.values():
                if lab.get("value"):
                    out[qid] = lab["value"]
                    break
    return out


def search_wikidata(name: str, limit: int = 3) -> list[dict]:
    """Search Wikidata for entities matching the given name."""
    params = {
        "action": "wbsearchentities",
        "search": name,
        "language": "en",
        "type": "item",
        "limit": limit,
        "format": "json",
    }
    r = requests.get(API, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json().get("search", [])


def names_match(yaml_name: str, wd_label: str) -> bool:
    """Loose comparison: case-insensitive, allow minor differences."""
    a = yaml_name.lower().strip()
    b = wd_label.lower().strip()
    if a == b:
        return True
    if a in b or b in a:
        return True
    return SequenceMatcher(None, a, b).ratio() >= 0.75


def main(path: str = "./composers.yaml") -> None:
    with open(path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        print("Top-level YAML is not a mapping – nothing to check.")
        return

    # URL validation
    url_errors = []
    for key, entry in data.items():
        if not isinstance(entry, dict):
            continue
        for field in URL_FIELDS:
            val = entry.get(field)
            if val is None:
                continue
            val = str(val)
            if not is_valid_url(val):
                url_errors.append((key, field, val))

    if url_errors:
        print(f"=== {len(url_errors)} invalid URL(s) ===\n")
        for key, field, val in url_errors:
            print(f"  [{key}] {field}: {val!r}")
        print()

    # Wikidata QID validation
    entries = {}  # key -> (name, qid)
    for key, entry in data.items():
        if not isinstance(entry, dict):
            continue
        qid = str(entry.get("wikidata", "")).strip()
        if qid.startswith("Q") and qid[1:].isdigit():
            entries[key] = (str(entry.get("name", "")), qid)

    if not entries:
        print("No Wikidata QIDs found.")
        return

    # Batch-fetch English labels (API supports up to 50 per request)
    all_qids = [qid for _, qid in entries.values()]
    en_labels = {}
    for i in range(0, len(all_qids), 50):
        batch = all_qids[i:i + 50]
        en_labels.update(get_wikidata_labels(batch, languages="en"))

    # Fallback: fetch any-language labels for QIDs missing English
    missing = [qid for _, qid in entries.values() if not en_labels.get(qid)]
    any_labels = {}
    if missing:
        for i in range(0, len(missing), 50):
            batch = missing[i:i + 50]
            any_labels.update(get_wikidata_labels(batch, languages=None))

    # Compare
    mismatches = []
    for key, (yaml_name, qid) in entries.items():
        wd_label = en_labels.get(qid) or any_labels.get(qid, "")
        if not wd_label:
            mismatches.append((key, yaml_name, qid, "(no label found)"))
        elif not names_match(yaml_name, wd_label):
            mismatches.append((key, yaml_name, qid, wd_label))

    # Remove false positives:
    # If the original QID is among its own search suggestions,
    # it's probably fine (e.g., Schumann vs Wieck maiden name etc.).
    confirmed = []
    for m in mismatches:
        key, yaml_name, qid, wd_label = m
        suggestions = search_wikidata(yaml_name)
        if any(s["id"] == qid for s in suggestions):
            continue  # original QID is a top result, not a real mismatch
        confirmed.append((key, yaml_name, qid, wd_label, suggestions))

    if confirmed:
        print(f"=== {len(confirmed)} Wikidata mismatch(es) ===\n")
        for key, yaml_name, qid, wd_label, suggestions in confirmed:
            print(f"  [{key}] YAML name: {yaml_name!r}")
            print(f"          Wikidata {qid}: {wd_label!r}")
            print(f"          https://www.wikidata.org/wiki/{qid}")
            if suggestions:
                print("          Suggested matches:")
                for s in suggestions:
                    desc = s.get("description", "")
                    print(f"            {s['id']}  {s['label']} – {desc}")
            print()
    else:
        print("All Wikidata QIDs match their YAML names.")


if __name__ == "__main__":
    main()
