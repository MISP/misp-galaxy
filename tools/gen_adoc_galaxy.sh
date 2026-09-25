#!/bin/bash
set -euo pipefail

cd "${0%/*}"

# Build into a scratch directory so a failed run cannot leave stale artifacts
# behind for the copy/scp steps below to publish.
workdir="$(mktemp -d)"
trap 'rm -rf "${workdir}"' EXIT

python3 adoc_galaxy.py > "${workdir}/a.txt"
asciidoctor -a allow-uri-read -o "${workdir}/a.html" "${workdir}/a.txt"
asciidoctor-pdf -a allow-uri-read -o "${workdir}/a.pdf" "${workdir}/a.txt"

# Every step above succeeded (set -e), so these artifacts are current.
cp "${workdir}/a.html" ../../misp-website/static/galaxy.html
cp "${workdir}/a.pdf"  ../../misp-website/static/galaxy.pdf
scp -l 81920 "${workdir}/a.html" circl@cpab.circl.lu:/var/www/nwww.circl.lu/doc/misp-galaxy/index.html
scp -l 81920 "${workdir}/a.pdf"  circl@cpab.circl.lu:/var/www/nwww.circl.lu/doc/misp-galaxy/galaxy.pdf
