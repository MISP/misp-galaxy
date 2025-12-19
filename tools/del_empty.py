#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def clean_synonyms(data: dict) -> bool:
    """
    Remove empty or whitespace-only strings from meta.synonyms arrays.
    Returns True if any change was made.
    """
    changed = False

    for entry in data.get("values", []):
        meta = entry.get("meta", {})
        synonyms = meta.get("synonyms")

        if isinstance(synonyms, list):
            cleaned = [s for s in synonyms if isinstance(s, str) and s.strip()]
            if cleaned != synonyms:
                meta["synonyms"] = cleaned
                changed = True

    return changed


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <json_file>", file=sys.stderr)
        sys.exit(1)

    path = Path(sys.argv[1])

    if not path.is_file():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    changed = clean_synonyms(data)

    if changed:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[+] Cleaned empty synonyms in {path}")
    else:
        print(f"[=] No changes needed in {path}")


if __name__ == "__main__":
    main()

