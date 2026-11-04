#!/bin/bash
set -euo pipefail
cd "${0%/*}"

# Stage the whole update in a temp file. clusters/malpedia.json is only
# replaced once the download, the sanity check and every cleanup script have
# all succeeded, so a failed fetch or a crashing cleanup cannot leave the
# committed cluster overwritten or half-processed.
tmp="$(mktemp malpedia.json.XXXXXX)"
trap 'rm -f "$tmp"' EXIT

curl --fail --show-error --silent -H 'Authorization: apitoken cdc3dad045375c027c3e5568c9067252fba1a56f' https://malpedia.caad.fkie.fraunhofer.de/api/get/misp -o "$tmp"

# An API error page can still be well-formed JSON, so check for the shape of
# a galaxy cluster rather than merely for parseable JSON.
if ! jq -e '(.values | type == "array") and (.values | length > 0)' "$tmp" >/dev/null 2>&1; then
    echo "ERROR: Malpedia response is not a populated galaxy cluster; clusters/malpedia.json left unchanged" >&2
    exit 1
fi

./del_duplicate_refs.py "$tmp"
./del_duplicate_uuids.py "$tmp"
./del_duplicate_value.py "$tmp"
./del_empty.py "$tmp"

mv "$tmp" ../clusters/malpedia.json
trap - EXIT

(cd ..; ./jq_all_the_things.sh)
