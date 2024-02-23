#!/bin/bash

requirements_path="requirements.txt"

pip freeze > installed.txt
diff -u <(sort $requirements_path) <(sort installed.txt)

if [ $? -eq 0 ]; then
    echo "All dependencies are installed with correct versions."
else
    echo "Dependencies missing or with incorrect versions. Please install all dependencies from $requirements_path into your environment."
    rm installed.txt # Clean up
#    exit 1
fi

rm installed.txt # Clean up

python3 generator.py
cd ./site/ || exit
mkdocs build
rsync --include ".*" -avh --delete -rz --checksum site/ circl@cppz.circl.lu:/var/www/misp-galaxy.org
