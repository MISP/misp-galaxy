#!/usr/bin/env python3
"""
audit_scor_uuid_relationships.py

SCOR-only UUID & relationship auditor for MISP-galaxy style files.

What it checks (SCOR files only):
  1) UUIDs exist, are lowercase, and look like RFC4122 v4/v5.
  2) UUIDs are unique across all SCOR clusters/galaxies.
  3) Each edge in values[*].related points to a known UUID; otherwise it's reported.
  4) Optional: reciprocal edges for symmetric relationship types.

Assumptions about data:
  - SCOR content lives in files whose basenames start with 'scor-' under clusters/ or galaxies/.
  - Cluster entries live at top-level key 'values' (standard MISP galaxy format).
  - Relationships live in entry['related'] as a list of dicts.
    Expected keys per relation (any of):
      - 'dest-uuid' or 'uuid' (destination UUID)
      - 'type' (string), optional but recommended

Usage:
  python3 tools/audit_scor_uuid_relationships.py --repo-root .
  python3 tools/audit_scor_uuid_relationships.py --repo-root . --require-reciprocal
  python3 tools/audit_scor_uuid_relationships.py --repo-root . --json

Exit codes:
  0 = all good (or only warnings when --fail-on-warn not set)
  1 = errors found (or warnings treated as errors via --fail-on-warn)
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

SCOR_PATH_PATTERNS = (
    ("clusters", "scor-"),
    ("galaxies", "scor-"),
)

# Reciprocal type map. Symmetric types map to themselves.
RECIPROCALS = {
    "related-to": "related-to",
    "similar-to": "similar-to",
    "maps-to": "maps-to",
    # Directed pairs:
    "part-of": "has-part",
    "has-part": "part-of",
    "subtechnique-of": "has-subtechnique",
    "has-subtechnique": "subtechnique-of",
}

def find_scor_files(repo_root: Path) -> List[Path]:
    files: List[Path] = []
    for base, prefix in SCOR_PATH_PATTERNS:
        d = repo_root / base
        if not d.is_dir():
            continue
        for p in sorted(d.glob(f"{prefix}*.json")):
            files.append(p)
    return files

def load_json(p: Path) -> Any:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"Failed to parse JSON: {p} ({e})") from e

def iter_cluster_entries(doc: Any, file_path: Path):
    """
    Yield (entry, file_path, cluster_name) for each values[*] entry.
    """
    values = doc.get("values")
    if not isinstance(values, list):
        return
    cluster_name = doc.get("name") or doc.get("namespace") or file_path.stem
    for entry in values:
        if isinstance(entry, dict):
            yield entry, file_path, cluster_name

def extract_rel_edges(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    rel = entry.get("related")
    if not isinstance(rel, list):
        return []
    edges: List[Dict[str, Any]] = []
    for r in rel:
        if not isinstance(r, dict):
            continue
        dest = r.get("dest-uuid") or r.get("uuid")
        rtype = r.get("type")
        if isinstance(dest, str):
            edges.append({"dest": dest, "type": rtype})
    return edges

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", help="Path to repo root")
    ap.add_argument("--require-reciprocal", action="store_true", help="Warn if symmetric/directed pairs lack a reciprocal")
    ap.add_argument("--reciprocal-types", default=",".join(sorted(RECIPROCALS.keys())),
                    help="Comma-separated relationship types to enforce reciprocals for")
    ap.add_argument("--json", action="store_true", help="Emit JSON report")
    ap.add_argument("--fail-on-warn", action="store_true", help="Treat warnings as errors")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    files = find_scor_files(repo_root)
    if not files:
        print("No SCOR files found under clusters/ or galaxies/.", file=sys.stderr)
        sys.exit(1)

    # Pass 1: collect entries and validate UUID shapes / lowercase / uniqueness
    uuid_to_entry: Dict[str, Dict[str, Any]] = {}
    errors: List[str] = []
    warnings: List[str] = []

    for p in files:
        doc = load_json(p)
        for entry, fpath, cluster_name in iter_cluster_entries(doc, p):
            u = entry.get("uuid")
            if not isinstance(u, str) or not u:
                errors.append(f"[MISSING-UUID] {fpath} :: {cluster_name} :: entry missing 'uuid'")
                continue
            if u != u.lower():
                errors.append(f"[UPPERCASE-UUID] {fpath} :: {cluster_name} :: {u}")
            if not UUID_RE.match(u):
                errors.append(f"[BAD-UUID-FORMAT] {fpath} :: {cluster_name} :: {u}")
            if u in uuid_to_entry:
                errors.append(f"[DUP-UUID] {u} present in {uuid_to_entry[u]['file']} and {fpath}")
            uuid_to_entry[u] = {
                "file": str(fpath),
                "cluster": cluster_name,
                "entry": entry,
            }

    # Pass 2: relationship audit within SCOR graph
    # Build adjacency for reciprocal checks
    edges: Dict[str, List[Tuple[str, str]]] = {}  # src -> [(dest, type)]
    for u, info in uuid_to_entry.items():
        entry = info["entry"]
        for e in extract_rel_edges(entry):
            dest = e["dest"]
            rtype = e.get("type") or ""
            # existence
            if dest not in uuid_to_entry:
                warnings.append(f"[EXT-OR-MISSING] {u} -> {dest} type='{rtype}' (dest not found in SCOR set)")
            # record edge regardless; helps reciprocal pass distinguish internal vs external
            edges.setdefault(u, []).append((dest, rtype))

    # Pass 3: optional reciprocal enforcement
    if args.require_reciprocal:
        # parse types to enforce
        to_enforce = set([t.strip() for t in args.reciprocal_types.split(",") if t.strip()])
        for src, out_edges in edges.items():
            for dest, rtype in out_edges:
                if rtype not in to_enforce:
                    continue
                recip = RECIPROCALS.get(rtype)
                if not recip:
                    continue
                # only enforce when both nodes are inside SCOR set
                if dest not in uuid_to_entry:
                    continue
                back_edges = edges.get(dest, [])
                if (src, recip) not in back_edges:
                    warnings.append(
                        f"[MISSING-RECIPROCAL] {src} -[{rtype}]-> {dest} "
                        f"but no {dest} -[{recip}]-> {src}"
                    )

    # Report
    summary = {
        "files_scanned": [str(p) for p in files],
        "scor_nodes": len(uuid_to_entry),
        "edge_count": sum(len(v) for v in edges.values()),
        "errors": errors,
        "warnings": warnings,
        "ok": not errors and not warnings,
        "ok_ignoring_warnings": not errors,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print("\nSCOR UUID/Relationship Audit\n" + "=" * 32)
        print(f"Files scanned: {len(files)}")
        print(f"SCOR nodes:    {summary['scor_nodes']}")
        print(f"Edges found:   {summary['edge_count']}\n")

        if errors:
            print("Errors:")
            for e in errors:
                print("  ❌", e)
            print()
        if warnings:
            print("Warnings:")
            for w in warnings:
                print("  ⚠️ ", w)
            print()

        if not errors and not warnings:
            print("✅ All SCOR UUIDs and relationships look good.")
        elif not errors:
            print("✅ No errors. ⚠️ Warnings present.")
        else:
            print("❌ Errors present.")

    exit_bad = bool(errors) or (args.fail_on_warn and bool(warnings))
    sys.exit(1 if exit_bad else 0)

if __name__ == "__main__":
    main()

