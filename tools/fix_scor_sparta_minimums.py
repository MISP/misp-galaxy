#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, json, pathlib, shutil, sys, time

# Canonical SCOR/SPARTA defaults
DEFAULT_AUTHORS = ["Aerospace Corporation"]
DEFAULT_CATEGORY = "SCOR"
DEFAULT_SOURCE = "https://sparta.aerospace.org/"

TARGET_BASENAMES = {
    "scor-sparta-tactics",
    "scor-sparta-techniques",
    "scor-sparta-mitigations",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", help="Path to misp-galaxy repo root")
    ap.add_argument("--authors", default=";".join(DEFAULT_AUTHORS),
                    help="Semicolon-separated authors to use if missing")
    ap.add_argument("--category", default=DEFAULT_CATEGORY, help="Category to use if missing")
    ap.add_argument("--source", default=DEFAULT_SOURCE, help="Source to use if missing")
    ap.add_argument("--dry-run", action="store_true", help="Show what would change")
    args = ap.parse_args()

    root = pathlib.Path(args.repo_root).resolve()
    clusters_dir = root / "clusters"
    problems = 0
    changes = 0

    authors = [a.strip() for a in args.authors.split(";") if a.strip()]
    category = args.category
    source = args.source

    for p in clusters_dir.glob("scor-sparta-*.json"):
        if p.stem not in TARGET_BASENAMES:
            continue

        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"ERROR: JSON parse failed for {p}: {e}")
            problems += 1
            continue

        before = json.dumps(data, sort_keys=True)

        # Only add if missing; never overwrite
        if "authors" not in data:
            data["authors"] = authors
        if "category" not in data:
            data["category"] = category
        if "source" not in data:
            data["source"] = source

        after = json.dumps(data, sort_keys=True)
        if before != after:
            changes += 1
            if args.dry_run:
                print(f"[DRY-RUN] Would add missing fields to {p}")
            else:
                ts = time.strftime("%Y%m%d-%H%M%S")
                bak = p.with_suffix(p.suffix + f".{ts}.bak")
                shutil.copy2(p, bak)
                p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                print(f"Updated {p} (backup: {bak.name})")
        else:
            print(f"No changes needed: {p}")

    if problems:
        sys.exit(1)
    print(f"Done. Files changed: {changes}")
    sys.exit(0)

if __name__ == "__main__":
    main()

