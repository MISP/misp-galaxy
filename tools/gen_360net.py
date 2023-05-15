#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#    A simple convertor of the https://apt.360.net to a MISP Galaxy datastructure.
#    Copyright (C) 2022 MISP Project
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import uuid
import json
import requests

import argparse

parser = argparse.ArgumentParser(description="Create the 360.net APTlist based on their website data.")
args = parser.parse_args()

r = requests.get("https://apt.360.net/apts/list", timeout=5)
list_data = r.json()

clusters = []
for actor in list_data['data']['list']:
    country_code = actor['location']['code']  # LATER find a magic way to convert this to a 2-letter country code
    try:
        refs = [actor['article']['full_url']]
    except TypeError:
        refs = []
    for ref in actor['recommends']:
        refs.append(ref['url'])
    refs = sorted(list(set(refs)))
    cluster = {
        'value': f"{actor['name']} - {actor['code']}",
        'description': actor['description'],
        'uuid': str(uuid.uuid5(uuid.UUID("9319371e-2504-4128-8410-3741cebbcfd3"), actor['code'])),
        'meta': {
            'synonyms': actor['alias'],
            'country': country_code,
            'refs': refs,
        }
    }
    if actor['attack_industry']:
        cluster['meta']['target-category'] = [i for i in actor['attack_industry'] if i]
    if actor['attack_region']:
        cluster['meta']['suspected-victims'] = [i for i in actor['attack_region'] if i]
    # LATER find a way to convert attack-method to MITRE ATT&CK
    clusters.append(cluster)

json_galaxy = {
    'icon': "user-secret",
    'name': "360.net Threat Actors",
    'description': "Known or estimated adversary groups as identified by 360.net.",
    'namespace': "360net",
    'type': "360net-threat-actor",
    'uuid': "20de4abf-f000-48ec-a929-3cdc5c2f3c23",
    'version': 1
}

with open(os.path.join('..', 'clusters', '360net.json'), 'r') as f:
    json_cluster = json.load(f)
json_cluster['values'] = clusters
json_cluster['version'] += 1

# save the Galaxy and Cluster file
with open(os.path.join('..', 'galaxies', '360net.json'), 'w') as f:
    json.dump(json_galaxy, f, indent=2, sort_keys=True, ensure_ascii=False)
    f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things

with open(os.path.join('..', 'clusters', '360net.json'), 'w') as f:
    json.dump(json_cluster, f, indent=2, sort_keys=True, ensure_ascii=False)
    f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things

print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh.")
