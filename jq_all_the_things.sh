#!/bin/bash

set -e
set -x

# Seeds sponge, from moreutils

for dir in clusters/*.json
do
    cat ${dir} | jq . | sponge ${dir}
done

for dir in galaxies/*.json
do
    cat ${dir} | jq . | sponge ${dir}
done

cat schema_clusters.json | jq . | sponge schema_clusters.json
cat schema_galaxies.json | jq . | sponge schema_galaxies.json
