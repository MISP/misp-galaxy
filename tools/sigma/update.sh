#!/bin/bash
rm -rf sigma
git clone https://github.com/SigmaHQ/sigma 
python3 sigma-to-galaxy.py -r -p ./sigma/rules
cat sigma-cluster.json | jq -S . >../../clusters/sigma-rules.json
