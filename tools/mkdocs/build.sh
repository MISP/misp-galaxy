#!/bin/bash

# Check if npm is installed
if ! [ -x "$(command -v npm)" ]; then
  echo 'Error: npm is not installed.' >&2
  exit 1
fi

python3 generator.py
pushd ./site/docs || exit
npm install
popd || exit
cd ./site/ || exit
mkdocs build
rsync --include ".*" -v -rz --checksum site/ circl@cppz.circl.lu:/var/www/misp-galaxy.org
