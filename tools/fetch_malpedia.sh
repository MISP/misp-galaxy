#!/bin/bash
cd "${0%/*}"
curl -H 'Authorization: apitoken <TOKEN>' https://malpedia.caad.fkie.fraunhofer.de/api/get/misp >malpedia.json
mv malpedia.json ../clusters/malpedia.json
./del_duplicate_refs.py ../clusters/malpedia.json
./del_duplicate_uuids.py ../clusters/malpedia.json
./del_duplicate_value.py ../clusters/malpedia.json
./del_empty.py ../clusters/malpedia.json
(cd ..; ./jq_all_the_things.sh)
