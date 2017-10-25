#!/bin/bash

# This file launch all validation of the jsons and schemas
# By default, It stop on file not commited.

# you could test with command ./validate_all.sh something


# Check Jsons format, and beautify
./jq_all_the_things.sh
rc=$?
if [[ $rc != 0 ]]; then
    exit $rc
fi

set -e
set -x

diffs=`git status --porcelain | wc -l`
if ! [ $diffs -eq 0 ]; then
  echo "Please make sure you run ./jq_all_the_things.sh before commiting."
  if [ $# -eq 0 ]; then
    exit 1
  fi
fi


# remove the exec flag on the json files
find -name "*.json" -exec chmod -x "{}" \;

diffs=`git status --porcelain | wc -l`

if ! [ $diffs -eq 0 ]; then
    echo "Please make sure you run remove the executable flag on the json files before commiting: find -name "*.json" -exec chmod -x \"{}\" \\;"
    exit 1
fi


# Validate schemas
for dir in clusters/*.json
do
  echo -n "${dir}: "
  jsonschema -i ${dir} schema_clusters.json
  rc=$?
  if [[ $rc != 0 ]]; then
    echo "Error on ${dir}"
    exit $rc
  fi
  echo ''
done

for dir in galaxies/*.json
do
  echo -n "${dir}: "
  jsonschema -i ${dir} schema_galaxies.json
  rc=$?
  if [[ $rc != 0 ]]; then
    echo "Error on ${dir}"
    exit $rc
  fi
  echo ''
done

for dir in misp/*.json
do
  echo -n "${dir}: "
  jsonschema -i ${dir} schema_misp.json
  rc=$?
  if [[ $rc != 0 ]]; then
    echo "Error on ${dir}"
    exit $rc
  fi
  echo ''
done

for dir in vocabularies/*/*.json
do
  echo -n "${dir}: "
  jsonschema -i ${dir} schema_vocabularies.json
  rc=$?
  if [[ $rc != 0 ]]; then
    echo "Error on ${dir}"
    exit $rc
  fi
  echo ''
done
