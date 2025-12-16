#!/bin/bash
cd "${0%/*}"
wget -O malpedia.json https://malpedia.caad.fkie.fraunhofer.de/api/get/misp
mv malpedia.json ../clusters/malpedia-notfix.json
# quickfix see : https://github.com/MISP/misp-galaxy/pull/1116
cat ../clusters/malpedia-notfix.json | grep -ev '[ ][ ][ ][ ]"",' > ../clusters/malpedia.json
rm ../clusters/malpedia-notfix.json
./del_duplicate_refs.py ../clusters/malpedia.json
./del_duplicate_uuids.py ../clusters/malpedia.json
(cd ..; ./jq_all_the_things.sh)
