#!/usr/bin/env python3
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path


_WS_RE = re.compile(r"\s+")


def norm_value(v: object) -> str | None:
    """
    Normalized dedupe key for entry['value'].
    Handles tricky duplicates caused by Unicode + invisible chars + whitespace variants.
    """
    if not isinstance(v, str):
        return None

    s = unicodedata.normalize("NFKC", v)

    # Remove common invisible characters
    s = s.replace("\u200b", "")  # ZERO WIDTH SPACE
    s = s.replace("\ufeff", "")  # BOM

    # Normalize whitespace
    s = s.strip()
    s = _WS_RE.sub(" ", s)

    # Normalize spaces just inside parentheses
    s = s.replace("( ", "(").replace(" )", ")")

    if not s:
        return None
    return s.casefold()


def refs_count(entry: dict) -> int:
    meta = entry.get("meta") or {}
    refs = meta.get("refs", [])
    return len(refs) if isinstance(refs, list) else 0


def synonyms_count(entry: dict) -> int:
    meta = entry.get("meta") or {}
    syn = meta.get("synonyms", [])
    if not isinstance(syn, list):
        return 0
    return sum(1 for s in syn if isinstance(s, str) and s.strip())


def desc_len(entry: dict) -> int:
    d = entry.get("description", "")
    return len(d.strip()) if isinstance(d, str) else 0


def score(entry: dict) -> tuple[int, int, int]:
    # Higher is better: refs > synonyms > description
    return (refs_count(entry), synonyms_count(entry), desc_len(entry))


def dedupe_keep_best(data: dict, debug_value: str | None = None) -> tuple[bool, dict]:
    values = data.get("values", [])
    if not isinstance(values, list):
        return False, {"error": "data['values'] is not a list"}

    debug_key = norm_value(debug_value) if debug_value else None

    best_by_key: dict[str, dict] = {}
    order: list[str] = []
    invalid_entries: list[dict] = []

    duplicates_seen = 0
    replaced = 0
    debug_hits = []

    for entry in values:
        raw_value = entry.get("value")
        key = norm_value(raw_value)

        if key is None:
            invalid_entries.append(entry)
            continue

        if debug_key is not None and key == debug_key:
            debug_hits.append(
                {
                    "raw_value_repr": repr(raw_value),
                    "norm_key": key,
                    "refs": refs_count(entry),
                    "synonyms": synonyms_count(entry),
                    "desc_len": desc_len(entry),
                    "uuid": entry.get("uuid"),
                }
            )

        if key not in best_by_key:
            best_by_key[key] = entry
            order.append(key)
            continue

        duplicates_seen += 1
        cur = best_by_key[key]
        if score(entry) > score(cur):
            best_by_key[key] = entry
            replaced += 1
        # ties -> keep first (stable)

    new_values = [best_by_key[k] for k in order] + invalid_entries

    changed = (len(new_values) != len(values)) or (replaced > 0)
    if changed:
        data["values"] = new_values

    stats = {
        "original_count": len(values),
        "new_count": len(new_values),
        "duplicates_seen": duplicates_seen,
        "replaced_with_better_entry": replaced,
        "invalid_value_entries_kept": len(invalid_entries),
        "unique_normalized_values": len(order),
    }

    if debug_key is not None:
        kept = best_by_key.get(debug_key)
        stats["debug"] = {
            "query": debug_value,
            "normalized_key": debug_key,
            "hits": debug_hits,
            "kept_uuid": kept.get("uuid") if isinstance(kept, dict) else None,
            "kept_refs": refs_count(kept) if isinstance(kept, dict) else None,
        }

    return changed, stats


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Deduplicate Malpedia-style JSON values[] by normalized value, keeping most refs."
    )
    ap.add_argument("json_file", help="Path to the JSON file to rewrite in-place.")
    ap.add_argument("--debug", dest="debug_value", help="Print diagnostics for a specific value string.")
    ap.add_argument("--dry-run", action="store_true", help="Do not write file; only print stats.")
    args = ap.parse_args()

    path = Path(args.json_file)
    if not path.is_file():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    changed, stats = dedupe_keep_best(data, debug_value=args.debug_value)

    if args.dry_run:
        print("[i] Dry-run: not writing file.")
    elif changed:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[+] Deduplicated entries in {path}")
    else:
        print(f"[=] No duplicates removed in {path}")

    print("[i] Stats:", json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

