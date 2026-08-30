#!/bin/bash
set -euo pipefail

cd "${0%/*}"

requirements_path="requirements.txt"

# Report any requirement that is missing or version-mismatched in the current
# environment. `pip freeze` lists everything installed, so a plain diff against
# requirements.txt is noise in any real virtualenv -- check containment instead.
missing="$(comm -23 <(LC_ALL=C sort -u "$requirements_path") <(pip freeze | LC_ALL=C sort -u))"
if [ -n "$missing" ]; then
    echo "Dependencies missing or with incorrect versions. Please install all dependencies from $requirements_path into your environment:" >&2
    echo "$missing" >&2
    exit 1
fi
echo "All dependencies are installed with correct versions."

python3 generator.py
(cd ./site/ && mkdocs build)

# Only publish once the generator and the mkdocs build have both succeeded --
# `rsync --delete` against the live site is destructive, and an aborted build
# would otherwise mirror an empty or partial tree onto misp-galaxy.org.
if [ ! -d site/site ] || [ -z "$(ls -A site/site)" ]; then
    echo "ERROR: site/site is missing or empty after mkdocs build; refusing to rsync --delete to production." >&2
    exit 1
fi

rsync --include ".*" -avh --delete -rz --checksum site/site/ circl@cppz.circl.lu:/var/www/misp-galaxy.org
