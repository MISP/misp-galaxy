#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit SCOR galaxies/clusters against "Creating a MISP Galaxy, 101" guidance.

What it checks (scoped to SCOR only):
  - Files exist in both galaxies/ and clusters/ with the same base name (101: "The name of the JSON file in both directories needs to be the same.")
  - Galaxy required fields: namespace, uuid, description, name, type, version, icon
  - Cluster required fields: authors, category, description, name, source, type, uuid, version
  - type equality: galaxy.type == cluster.type == base filename (101: "type ... glues the galaxy file and cluster file together.")
  - UUIDs: present, lowercase, RFC4122 v4/v5 shape; uniqueness within SCOR set
  - Matrix semantics for matrix-style galaxies:
      * galaxy.kill_chain_order is a dict of tabs -> list of columns
      * every cluster value has description, value, uuid, meta
      * meta.kill_chain uses only declared tabs and columns
  - Relationship hygiene:
      * every SCOR value's uuid is unique across SCOR
      * warn if any SCOR file has extra keys missing from 101 minimal examples

Exit code: 0 on success, 1 if any errors were found.
"""

import argparse
import json
import pathlib
import re
import sys
from collections import defaultdict

SCOR_PREFIXES = (
    "scor-",
)

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

def is_scor_file(p: pathlib.Path) -> bool:
    name = p.name
    return name.startswith(SCOR_PREFIXES)

def load_json(p: pathlib.Path):
    try:
        return json.loads(p.read_text(encoding="utf-8")), None
    except Exception as e:
        return None, f"JSON parse error: {e}"

def expect(cond, bucket, msg):
    if cond:
        bucket["ok"].append(msg)
    else:
        bucket["err"].append(msg)

def warn(cond, bucket, msg):
    if cond:
        bucket["ok"].append(msg)
    else:
        bucket["warn"].append(msg)

def uuid_ok(u: str) -> bool:
    return isinstance(u, str) and UUID_RE.match(u) is not None and u == u.lower()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", help="Path to misp-galaxy repo root")
    ap.add_argument("--require-reciprocal", action="store_true",
                    help="Reserved flag, not used for 101 checks; kept for parity with prior tooling.")
    args = ap.parse_args()

    root = pathlib.Path(args.repo_root).resolve()
    galaxies_dir = root / "galaxies"
    clusters_dir = root / "clusters"

    results = defaultdict(lambda: {"ok": [], "warn": [], "err": []})
    all_node_uuids = {}
    all_value_uuids = {}

    # Discover SCOR pairs by base name present in either dir and limited to SCOR
    galaxy_files = {p.stem: p for p in galaxies_dir.glob("*.json") if is_scor_file(p)}
    cluster_files = {p.stem: p for p in clusters_dir.glob("*.json") if is_scor_file(p)}
    basenames = sorted(set(galaxy_files) | set(cluster_files))

    total_files = 0
    for base in basenames:
        if not (base in galaxy_files and base in cluster_files):
            # Only consider bases that are SCOR; if one side missing, flag error
            r = results[base]
            if base not in galaxy_files:
                r["err"].append(f"Missing galaxies/{base}.json")
            if base not in cluster_files:
                r["err"].append(f"Missing clusters/{base}.json")
            continue

        gpath = galaxy_files[base]
        cpath = cluster_files[base]
        total_files += 2

        r = results[base]

        g, ge = load_json(gpath)
        c, ce = load_json(cpath)
        if ge:
            r["err"].append(f"{gpath}: {ge}")
            continue
        if ce:
            r["err"].append(f"{cpath}: {ce}")
            continue

        # Galaxy required fields
        g_required = ["namespace", "uuid", "description", "name", "type", "version", "icon"]
        for k in g_required:
            expect(k in g, r, f"Galaxy has '{k}'")

        # Cluster required fields
        c_required = ["authors", "category", "description", "name", "source", "type", "uuid", "version"]
        for k in c_required:
            expect(k in c, r, f"Cluster has '{k}'")

        # type glue and filename agreement
        expect("type" in g and "type" in c, r, "Both galaxy and cluster define 'type'")
        if "type" in g and "type" in c:
            expect(g["type"] == c["type"], r, f"type matches between galaxy and cluster ({g.get('type')})")
            expect(g["type"] == base, r, f"type equals base filename '{base}'")

        # UUID checks
        if "uuid" in g:
            expect(uuid_ok(g["uuid"]), r, f"Galaxy uuid is lowercase RFC4122 v4/v5 form")
            if g["uuid"] in all_node_uuids:
                r["err"].append(f"Galaxy uuid duplicates {all_node_uuids[g['uuid']]}")
            else:
                all_node_uuids[g["uuid"]] = f"galaxies/{base}.json"
        if "uuid" in c:
            expect(uuid_ok(c["uuid"]), r, f"Cluster uuid is lowercase RFC4122 v4/v5 form")
            if c["uuid"] in all_node_uuids:
                r["err"].append(f"Cluster uuid duplicates {all_node_uuids[c['uuid']]}")
            else:
                all_node_uuids[c["uuid"]] = f"clusters/{base}.json"

        # Detect matrix galaxy by presence of kill_chain_order
        is_matrix = "kill_chain_order" in g
        tabs = set()
        columns = set()
        if is_matrix:
            expect(isinstance(g["kill_chain_order"], dict), r, "kill_chain_order is a dict")
            for tab, cols in (g.get("kill_chain_order") or {}).items():
                tabs.add(tab)
                warn(isinstance(cols, list) and all(isinstance(x, str) for x in cols), r,
                     f"kill_chain_order['{tab}'] is a list[str]")
                if isinstance(cols, list):
                    columns.update(cols)
            expect(tabs and columns, r, "Matrix defines at least one tab and one column")

        # Cluster values checks
        values = c.get("values", [])
        expect(isinstance(values, list), r, "Cluster has 'values' as a list")

        for idx, val in enumerate(values):
            ctx = f"values[{idx}]"
            expect(isinstance(val, dict), r, f"{ctx} is an object")
            expect("uuid" in val and uuid_ok(val["uuid"]), r, f"{ctx} has lowercase RFC4122 uuid")
            expect("description" in val and isinstance(val["description"], str), r, f"{ctx} has description")
            expect("value" in val and isinstance(val["value"], str), r, f"{ctx} has value label")
            # uniqueness of value uuids across SCOR
            vu = val.get("uuid")
            if isinstance(vu, str):
                if vu in all_value_uuids:
                    r["err"].append(f"{ctx} uuid duplicates {all_value_uuids[vu]}")
                else:
                    all_value_uuids[vu] = f"clusters/{base}.json::{ctx}"

            # matrix semantics per 101: meta.kill_chain ["tab:column"]
            if is_matrix:
                meta = val.get("meta", {})
                expect(isinstance(meta, dict), r, f"{ctx} has 'meta'")
                kc = meta.get("kill_chain")
                expect(isinstance(kc, list) and all(isinstance(x, str) for x in kc), r,
                       f"{ctx} meta.kill_chain is a list[str]")
                if isinstance(kc, list):
                    for token in kc:
                        if ":" not in token:
                            r["err"].append(f"{ctx} kill_chain entry '{token}' missing 'tab:column'")
                            continue
                        tab, col = token.split(":", 1)
                        if tabs and tab not in tabs:
                            r["err"].append(f"{ctx} kill_chain tab '{tab}' not in galaxy tabs {sorted(tabs)}")
                        if columns and col not in columns:
                            r["err"].append(f"{ctx} kill_chain column '{col}' not in galaxy columns {sorted(columns)}")

        # Friendly warnings for fields often present in practice but not strictly required by 101
        # e.g., extra keys not shown in the blog examples
        # We just note them for reviewer awareness.
        allowed_galaxy_keys = {"namespace", "uuid", "description", "name", "type", "version", "icon", "kill_chain_order"}
        extra_g = set(g.keys()) - allowed_galaxy_keys
        if extra_g:
            r["warn"].append(f"Galaxy has additional fields not in 101 example: {sorted(extra_g)}")

        allowed_cluster_keys = {"authors", "category", "description", "name", "source", "type", "uuid", "version", "values"}
        extra_c = set(c.keys()) - allowed_cluster_keys
        if extra_c:
            r["warn"].append(f"Cluster has additional fields not in 101 example: {sorted(extra_c)}")

    # Print report
    scor_files = sum(1 for b in basenames if b in galaxy_files and b in cluster_files) * 2
    print("SCOR 101 Compliance Audit")
    print("=========================")
    print(f"Files scanned: {scor_files}")
    print(f"Unique SCOR node UUIDs: {len(all_node_uuids)}")
    print(f"Unique SCOR value UUIDs: {len(all_value_uuids)}")
    print()

    had_err = False
    for base in basenames:
        r = results[base]
        if not r["ok"] and not r["warn"] and not r["err"]:
            continue
        status = "✅ OK"
        if r["err"]:
            status = "❌ FAIL"
            had_err = True
        elif r["warn"]:
            status = "⚠️ WARN"
        print(f"[{status}] {base}")
        for m in r["err"]:
            print(f"  ERROR: {m}")
        for m in r["warn"]:
            print(f"  WARN:  {m}")
        for m in r["ok"]:
            print(f"  OK:    {m}")
        print()

    # Suggest running repo validators referenced by 101
    print("Next suggested steps (from 101):")
    print("  ./validate_all.sh  &&  ./jq_all_the_things.sh")
    sys.exit(1 if had_err else 0)

if __name__ == "__main__":
    main()

