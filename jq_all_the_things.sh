#!/bin/bash

# Seeds sponge, from moreutils

#Validate all Jsons first
for dir in `find . -name "*.json"`
do
  echo validating ${dir}
  cat ${dir} | jq . >/dev/null
  rc=$?
  if [[ $rc != 0 ]]; then exit $rc; fi
done

set -e
set -x

for dir in clusters/*.json
do
    # Beautify it
    cat ${dir} | jq . | sponge ${dir}
done

for dir in galaxies/*.json
do
    # Beautify it
    cat ${dir} | jq . | sponge ${dir}
done

cat schema_clusters.json | jq . | sponge schema_clusters.json
cat schema_galaxies.json | jq . | sponge schema_galaxies.json
