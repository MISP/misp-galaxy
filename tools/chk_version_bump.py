#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check that a cluster or galaxy whose content changed also bumped `version`.

MISP synchronises galaxies by version: an instance only re-imports a file
whose version is higher than the one it already holds. So content that
changes without the version moving never reaches instances that already have
the old copy -- the edit is committed here and invisible everywhere else.

It happens routinely. Walking first-parent history and comparing each file's
content with `version` removed, 685 commits across 70 files changed content
without bumping (threat-actor 315, ransomware 76, tool 53, rat 29).

This compares the working tree against a baseline revision and only looks at
files the change actually touches, so it never fails for history it did not
cause.

    tools/chk_version_bump.py                     # vs origin/main
    tools/chk_version_bump.py --baseline HEAD~1
"""

import argparse
import json
import os
import subprocess
import sys

WATCHED_DIRS = ("clusters", "galaxies")


def _repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)


def _content_without_version(doc):
    """A stable rendering of the document with `version` removed."""
    trimmed = {k: v for k, v in doc.items() if k != "version"}
    return json.dumps(trimmed, sort_keys=True, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--baseline", default="origin/main",
                        help="revision to compare against (default: origin/main)")
    args = parser.parse_args()
    root = _repo_root()

    changed = _git(root, "diff", "--name-only", args.baseline, "--", *WATCHED_DIRS)
    if changed.returncode != 0:
        print("Could not diff against %r:\n%s" % (args.baseline, changed.stderr.strip()))
        return 0
    paths = [p for p in changed.stdout.split() if p.endswith(".json")]

    if not paths:
        print("No cluster or galaxy files changed against %s." % args.baseline)
        return 0

    problems, ok = [], []
    for rel in paths:
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            continue  # deleted
        with open(path, encoding="utf-8") as f:
            new = json.load(f)
        blob = _git(root, "show", "%s:%s" % (args.baseline, rel))
        if blob.returncode != 0:
            ok.append((rel, "new file", None, new.get("version")))
            continue
        old = json.loads(blob.stdout)

        if _content_without_version(old) == _content_without_version(new):
            continue  # only the version (or nothing) changed

        old_v, new_v = old.get("version"), new.get("version")
        if isinstance(old_v, (int, float)) and isinstance(new_v, (int, float)) and new_v > old_v:
            ok.append((rel, "bumped", old_v, new_v))
        else:
            problems.append((rel, old_v, new_v))

    for rel, why, old_v, new_v in ok:
        print("  OK    %-56s %s (%s -> %s)" % (rel, why, old_v, new_v))
    for rel, old_v, new_v in problems:
        print("  FAIL  %-56s content changed, version %s -> %s" % (rel, old_v, new_v))

    if problems:
        print("\n%d file(s) changed content without increasing `version`.\n"
              "MISP only re-imports a galaxy whose version is higher than the one an\n"
              "instance already holds, so these edits will not reach existing instances."
              % len(problems))
        return 1

    if not ok:
        print("No content changes in clusters/ or galaxies/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
