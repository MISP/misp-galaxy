#!/bin/bash

requirements_path="requirements.txt"
missing_deps=0

while IFS= read -r line || [[ -n "$line" ]]; do
    echo "$line" | grep -F -f - <(pip freeze)
    if [ $? -ne 0 ]; then
        echo "Missing or incorrect version: $line"
        ((missing_deps++))
    fi
done < "$requirements_path"

if [ $missing_deps -eq 0 ]; then
    echo "All dependencies are installed with correct versions."
else
    echo "$missing_deps dependencies are missing or have incorrect versions."
    exit 1
fi

python3 generator.py
cd ./site/ || exit
mkdocs build
rsync --include ".*" -v -rz --checksum site/ circl@cppz.circl.lu:/var/www/misp-galaxy.org
