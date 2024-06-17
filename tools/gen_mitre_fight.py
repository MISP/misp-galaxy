#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    A simple convertor of the MITRE D3FEND to a MISP Galaxy datastructure.
#    Copyright (C) 2024 Christophe Vandeplas
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

import json
import os
import requests
import uuid
import yaml
from bs4 import BeautifulSoup
from markdown import markdown


uuid_seed = '8666d04b-977a-434b-82b4-f36271ec1cfb'

fight_url = 'https://fight.mitre.org/fight.yaml'

tactics = {}   # key = ID, value = tactic
phases_ids = []
techniques_ids = []
techniques = []
relations = {}


r = requests.get(fight_url)
fight = yaml.safe_load(r.text)

# with open('fight.yaml', 'w') as f:
#     f.write(r.text)
# with open('fight.yaml', 'r') as f:
#     fight = yaml.safe_load(f)


def clean_ref(text: str) -> str:
    '''
    '<a name="1"> \\[1\\] </a> [5GS Roaming Guidelines Version 5.0 (non-confidential), NG.113-v5.0, GSMA, December 2021](https://www.gsma.com/newsroom/wp-content/uploads//NG.113-v5.0.pdf)'
    '''
    html = markdown(text.replace('](', ' - ').replace(')', ' ').replace(' [', ''))
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text().strip()


# tactics
for item in fight['tactics']:
    tactics[item['id']] = item['name'].replace(' ', '-')

# techniques
for item in fight['techniques']:
    technique = {
        'value': item['name'],
        'description': item['description'],
        'uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), item['id'])),
        'meta': {
            'kill_chain': [],
            'refs': [f"https://fight.mitre.org/techniques/{item['id']}"],
            'external_id': item['id']
        },
        'related': []
    }
    keys_to_skip = ['id', 'name', 'references', 'tactics']
    for keys in item.keys():
        if keys not in keys_to_skip:
            technique['meta'][keys] = item[keys]

    try:
        for ref in item['references']:
            technique['meta']['refs'].append(clean_ref(ref))
    except KeyError:
        pass

    for tactic in item['tactics']:
        technique['meta']['kill_chain'].append(f"fight:{tactics[tactic]}")

    for mitigation in item['mitigations']:
        technique['meta']['refs'].append(f"https://fight.mitre.org/mitigations/{mitigation['fgmid']}")
        # add relationship
        technique['related'].append({
            'dest-uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), mitigation['fgmid'])),
            'type': 'mitigated-by'
        })

    for detection in item['detections']:
        technique['meta']['refs'].append(f"https://fight.mitre.org/data%20sources/{detection['fgdsid']}")
        # add relationship
        technique['related'].append({
            'dest-uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), detection['fgdsid'])),
            'type': 'detected-by'
        })

    try:
        technique['related'].append({
            'dest-uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), item['subtechnique-of'])),
            'type': 'subtechnique-of'
        })
    except KeyError:
        pass

    techniques.append(technique)


# TODO mitigations
# TODO data sources


kill_chain_tactics = {'fight': []}
for tactic_id, value in tactics.items():
    kill_chain_tactics['fight'].append(value)


galaxy_fname = 'mitre-fight.json'
galaxy_type = "mitre-fight"
galaxy_name = "MITRE FiGHT"
galaxy_description = 'MITRE Five-G Hierarchy of Threats (FiGHT™) is a globally accessible knowledge base of adversary tactics and techniques that are used or could be used against 5G networks.'
galaxy_source = 'https://fight.mitre.org/'
json_galaxy = {
    'description': galaxy_description,
    'icon': "user-shield",
    'kill_chain_order': kill_chain_tactics,
    'name': galaxy_name,
    'namespace': "mitre",
    'type': galaxy_type,
    'uuid': "c22c8c18-0ccd-4033-b2dd-804ad26af4b9",
    'version': 1
}

json_cluster = {
    'authors': ["MITRE"],
    'category': 'attach-pattern',
    'name': galaxy_name,
    'description': galaxy_description,
    'source': galaxy_source,
    'type': galaxy_type,
    'uuid': "6a1fa29f-85a5-4b1c-956b-ebb7df314486",
    'values': list(techniques),
    'version': 1
}


# save the Galaxy and Cluster file
with open(os.path.join('..', 'galaxies', galaxy_fname), 'w') as f:
    # sort_keys, even if it breaks the kill_chain_order , but jq_all_the_things requires sorted keys
    json.dump(json_galaxy, f, indent=2, sort_keys=True, ensure_ascii=False)
    f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things

with open(os.path.join('..', 'clusters', galaxy_fname), 'w') as f:
    json.dump(json_cluster, f, indent=2, sort_keys=True, ensure_ascii=False)
    f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things

print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh.")
