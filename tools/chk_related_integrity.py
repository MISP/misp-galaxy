#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check that every `related` edge points at a uuid that exists in this repo.

Nothing validates this today: `schema_clusters.json` can constrain the shape
of a `related` entry, but not whether its `dest-uuid` resolves. A typo, or a
value deleted while other clusters still reference it, produces a dangling
edge that no test catches. The documentation site renders those as "Private
Cluster" placeholders.

There is a pre-existing backlog of such edges, so a check that simply fails
on any dangling edge would leave CI permanently red. By default this
compares against a baseline revision and fails only on edges that are *new*
-- the backlog is reported but does not block. Run with --all to see the
whole picture.

    tools/chk_related_integrity.py                    # vs origin/main
    tools/chk_related_integrity.py --baseline HEAD~1
    tools/chk_related_integrity.py --all              # report everything
    tools/chk_related_integrity.py --all --strict     # and fail on it
"""

import argparse
import collections
import json
import os
import subprocess
import sys

# Directories whose files define uuids that a `related` edge may point at.
UUID_DIRS = ("clusters", "galaxies", "misp", "vocabularies")
EDGE_DIRS = ("clusters",)


def _repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _iter_json(root, subdir, ref=None):
    """Yield (relative path, parsed document) for a directory, at `ref` or on disk."""
    if ref is None:
        directory = os.path.join(root, subdir)
        if not os.path.isdir(directory):
            return
        for name in sorted(os.listdir(directory)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(directory, name)
            with open(path, encoding="utf-8") as f:
                try:
                    yield "%s/%s" % (subdir, name), json.load(f)
                except ValueError as exc:
                    raise SystemExit("%s: invalid JSON: %s" % (path, exc))
        return

    listing = subprocess.run(
        ["git", "-C", root, "ls-tree", "--name-only", "%s:%s" % (ref, subdir)],
        capture_output=True, text=True)
    if listing.returncode != 0:
        return
    for name in sorted(listing.stdout.split()):
        if not name.endswith(".json"):
            continue
        blob = subprocess.run(
            ["git", "-C", root, "show", "%s:%s/%s" % (ref, subdir, name)],
            capture_output=True, text=True)
        if blob.returncode != 0:
            continue
        try:
            yield "%s/%s" % (subdir, name), json.loads(blob.stdout)
        except ValueError:
            continue


def collect(root, ref=None):
    """Return (known uuids, dangling edges) for a revision.

    An edge is (source file, source value, source uuid, dest-uuid).
    """
    known = set()
    docs = {}
    for subdir in UUID_DIRS:
        for rel, doc in _iter_json(root, subdir, ref):
            docs[rel] = doc
            if isinstance(doc, dict):
                if doc.get("uuid"):
                    known.add(doc["uuid"])
                for value in doc.get("values") or []:
                    if isinstance(value, dict) and value.get("uuid"):
                        known.add(value["uuid"])

    dangling = []
    for rel, doc in docs.items():
        if not rel.startswith(tuple(d + "/" for d in EDGE_DIRS)):
            continue
        for value in doc.get("values") or []:
            if not isinstance(value, dict):
                continue
            for edge in value.get("related") or []:
                if not isinstance(edge, dict):
                    continue
                dest = edge.get("dest-uuid")
                if not dest or dest not in known:
                    dangling.append((rel, value.get("value"), value.get("uuid"), dest))
    return known, dangling


def report(title, edges, limit):
    print(title)
    if not edges:
        print("  none")
        return
    per_file = collections.Counter(e[0] for e in edges)
    for rel, count in per_file.most_common():
        print("  %-52s %5d" % (rel, count))
    print("  %stotal: %d edge(s), %d distinct missing uuid(s)"
          % ("", len(edges), len({e[3] for e in edges})))
    print()
    for rel, value, _src, dest in edges[:limit]:
        print("    %s: %r -> %s" % (rel, value, dest or "<empty>"))
    if len(edges) > limit:
        print("    ... and %d more" % (len(edges) - limit))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--baseline", default="origin/main",
                        help="revision to compare against (default: origin/main)")
    parser.add_argument("--all", action="store_true",
                        help="report every dangling edge, not only new ones")
    parser.add_argument("--strict", action="store_true",
                        help="with --all, fail if any dangling edge exists")
    parser.add_argument("--limit", type=int, default=20,
                        help="how many example edges to print (default: 20)")
    args = parser.parse_args()

    root = _repo_root()
    _known, current = collect(root)

    if args.all:
        report("Dangling `related` edges in the working tree:", current, args.limit)
        if current and args.strict:
            return 1
        return 0

    try:
        _baseline_known, baseline = collect(root, args.baseline)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - baseline is best-effort
        print("Could not read baseline %r (%s); checking every edge instead."
              % (args.baseline, exc))
        baseline = []

    previously = {(e[2], e[3]) for e in baseline}
    new = [e for e in current if (e[2], e[3]) not in previously]

    print("Dangling `related` edges: %d in the working tree, %d at %s\n"
          % (len(current), len(baseline), args.baseline))
    report("New in this change:", new, args.limit)

    if new:
        print("\nEach `related` entry above points at a uuid that does not exist in "
              "clusters/, galaxies/, misp/ or vocabularies/. Fix the dest-uuid, or "
              "remove the edge.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
