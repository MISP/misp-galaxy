#!/bin/bash

# Seeds sponge, from moreutils

#Validate all Jsons first
for dir in `find . -name "*.json"`
do
  echo validating ${dir}
  # python3 -c "import json; f_in = open('${dir}'); data = json.load(f_in); f_in.close(); f_out = open('${dir}', 'w'); json.dump(data, f_out, indent=2, sort_keys=True, ensure_ascii=False); f_out.close();"
  cat ${dir} | jq . >/dev/null
  rc=$?
  if [[ $rc != 0 ]]; then exit $rc; fi
done

set -e
set -x

for dir in clusters/*.json
do
    python3 tools/add_missing_uuid.py -f ${dir}
    # Beautify it
    cat ${dir} | jq --sort-keys . | sponge ${dir}
done

for dir in galaxies/*.json
do
    # Beautify it
    cat ${dir} | jq --sort-keys . | sponge ${dir}
done

cat schema_clusters.json | jq . | sponge schema_clusters.json
cat schema_galaxies.json | jq . | sponge schema_galaxies.json
