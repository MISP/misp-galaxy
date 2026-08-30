#!/bin/bash
set -euo pipefail

# Always operate relative to this script, so `rm -rf sigma` and the clone
# cannot land outside tools/sigma when invoked from another directory.
cd "${0%/*}"

rm -rf sigma
git clone https://github.com/SigmaHQ/sigma
python3 sigma-to-galaxy.py -r -p ./sigma/rules

# Write through a temp file: a failure in sigma-to-galaxy.py or jq must not
# truncate the committed cluster.
tmp="$(mktemp ../../clusters/sigma-rules.json.XXXXXX)"
if jq -S . sigma-cluster.json > "${tmp}"; then
    mv "${tmp}" ../../clusters/sigma-rules.json
else
    rm -f "${tmp}"
    echo "ERROR: jq failed on sigma-cluster.json, clusters/sigma-rules.json left unchanged" >&2
    exit 1
fi
