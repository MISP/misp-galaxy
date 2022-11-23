#!/bin/bash
cd "${0%/*}"
wget -O malpedia.json https://malpedia.caad.fkie.fraunhofer.de/api/get/misp
mv malpedia.json ../clusters/malpedia.json
./del_duplicate_refs.py ../clusters/malpedia.json
./del_duplicate_uuids.py ../clusters/malpedia.json
(cd ..; ./jq_all_the_things.sh)
