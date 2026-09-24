#!/bin/bash

# Validate all JSONs first in cluster and galaxy

folders=( clusters/*.json galaxies/*.json )
for dir in "${folders[@]}"
do
  echo validating ${dir}
  # python3 -c "import json; f_in = open('${dir}'); data = json.load(f_in); f_in.close(); f_out = open('${dir}', 'w'); json.dump(data, f_out, indent=2, sort_keys=True, ensure_ascii=False); f_out.close();"
  cat ${dir} | jq . >/dev/null
  rc=$?
  if [[ $rc != 0 ]]; then exit $rc; fi
done

set -e
set -o pipefail
set -x

# Beautify a JSON file in place, but only if jq actually succeeded.
# Writing through a temp file means a jq failure leaves the original intact
# instead of truncating it to 0 bytes.
beautify() {
    local target="$1"
    shift
    local tmp
    tmp="$(mktemp "${target}.XXXXXX")"
    if jq "$@" . "${target}" > "${tmp}"; then
        mv "${tmp}" "${target}"
    else
        rm -f "${tmp}"
        echo "ERROR: jq failed on ${target}, left unchanged" >&2
        return 1
    fi
}

for dir in clusters/*.json
do
    python3 tools/add_missing_uuid.py -f "${dir}"
    beautify "${dir}" --sort-keys
done

for dir in galaxies/*.json
do
    beautify "${dir}" --sort-keys
done

beautify schema_clusters.json
beautify schema_galaxies.json
