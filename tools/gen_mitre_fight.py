#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    A simple convertor of the MITRE FiGHT to a MISP Galaxy datastructure.
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

from bs4 import BeautifulSoup
from markdown import markdown
import json
import os
import re
import requests
import uuid
import yaml
from pymispgalaxies import Cluster, Galaxy

uuid_seed = '8666d04b-977a-434b-82b4-f36271ec1cfb'

fight_url = 'https://fight.mitre.org/fight.yaml'

galaxy_type = "mitre-fight"
galaxy_description = 'MITRE Five-G Hierarchy of Threats (FiGHT™) is a globally accessible knowledge base of adversary tactics and techniques that are used or could be used against 5G networks.'
galaxy_source = 'https://fight.mitre.org/'


r = requests.get(fight_url)
fight = yaml.safe_load(r.text)

# with open('fight.yaml', 'w') as f:
#     f.write(r.text)
# with open('fight.yaml', 'r') as f:
#     fight = yaml.safe_load(f)


mitre_attack_pattern = Cluster('mitre-attack-pattern')


def find_mitre_uuid_from_technique_id(technique_id):
    try:
        return mitre_attack_pattern.get_by_external_id(technique_id).uuid
    except KeyError:
        print("No MITRE UUID found for technique_id: ", technique_id)
        return None


def clean_ref(text: str) -> str:
    '''
    '<a name="1"> \\[1\\] </a> [5GS Roaming Guidelines Version 5.0 (non-confidential), NG.113-v5.0, GSMA, December 2021](https://www.gsma.com/newsroom/wp-content/uploads//NG.113-v5.0.pdf)'
    '''
    html = markdown(text.replace('](', ' - ').replace(')', ' ').replace(' [', ''))
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text().strip()


def save_galaxy_and_cluster(json_galaxy, json_cluster, galaxy_fname):
    # save the Galaxy and Cluster file
    with open(os.path.join('..', 'galaxies', galaxy_fname), 'w') as f:
        # sort_keys, even if it breaks the kill_chain_order , but jq_all_the_things requires sorted keys
        json.dump(json_galaxy, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things

    with open(os.path.join('..', 'clusters', galaxy_fname), 'w') as f:
        json.dump(json_cluster, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things


# tactics
tactics = {}   # key = ID, value = tactic
for item in fight['tactics']:
    tactics[item['id']] = item['name'].replace(' ', '-')

#
# techniques
#
technique_galaxy_name = "MITRE FiGHT Techniques"
technique_cluster = Cluster({
    'authors': ["MITRE"],
    'category': 'attack-pattern',
    'name': technique_galaxy_name,
    'description': galaxy_description,
    'source': galaxy_source,
    'type': galaxy_type,
    'uuid': "6a1fa29f-85a5-4b1c-956b-ebb7df314486",
    'version': 1
})

for item in fight['techniques']:
    technique_string = item['name'].strip().lower()
    element = {
        'value': item['name'].strip(),
        'description': item['description'].strip(),
        'uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), item['id'])),
        'meta': {
            'kill_chain': [],
            'refs': [f"https://fight.mitre.org/techniques/{item['id']}"],
            'external_id': item['id']
        },
        'related': []
    }
    keys_to_skip = ['id', 'name', 'references', 'tactics', 'description']
    for keys in item.keys():
        if keys not in keys_to_skip:
            element['meta'][keys] = item[keys]

    if 'https://attack.mitre.org/techniques/' in item['description']:
        # extract the references from the description
        # add it as ref and build the relationship to the technique using uuid
        url = re.search(r'(https?://[^\)]+)/(T[^\)]+)', item['description'])
        if url:
            extracted_url = url.group(0)
            element['meta']['refs'].append(extracted_url)
            technique_uuid = find_mitre_uuid_from_technique_id(url.group(2).replace('/', '.'))
            if technique_uuid:
                element['related'].append({
                    'dest-uuid': technique_uuid,
                    'type': 'related-to'
                })
            else:
                print("WARNING: No MITRE UUID found for technique_id: ", url.group(2))
        pass

    try:
        for ref in item['references']:
            element['meta']['refs'].append(clean_ref(ref))
    except KeyError:
        pass

    for tactic in item['tactics']:
        element['meta']['kill_chain'].append(f"fight:{tactics[tactic]}")

    for mitigation in item['mitigations']:
        element['meta']['refs'].append(f"https://fight.mitre.org/mitigations/{mitigation['fgmid']}")
        # add relationship
        element['related'].append({
            'dest-uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), mitigation['fgmid'])),
            'type': 'mitigated-by'
        })

    for detection in item['detections']:
        element['meta']['refs'].append(f"https://fight.mitre.org/data%20sources/{detection['fgdsid']}")
        # add relationship
        element['related'].append({
            'dest-uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), detection['fgdsid'])),
            'type': 'detected-by'
        })

    try:
        element['related'].append({
            'dest-uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), item['subtechnique-of'])),
            'type': 'subtechnique-of'
        })
    except KeyError:
        pass

    element['meta']['refs'] = list(set(element['meta']['refs']))
    element['meta']['refs'].sort()

    technique_cluster.append(element, skip_duplicates=True)

technique_cluster.save('mitre-fight-techniques')

for cluster, duplicate in technique_cluster.duplicates:
    print(f"Skipped duplicate: {duplicate} in cluster {cluster}")

kill_chain_tactics = technique_cluster.get_kill_chain_tactics()


try:
    technique_galaxy = Galaxy('mitre-fight-techniques')
    # check if new kill_chain_tactics are present, add them if needed
    for key, values in kill_chain_tactics.items():
        if key not in technique_galaxy.kill_chain_order:
            technique_galaxy.kill_chain_order[key] = []
        for value in values:
            if key not in technique_galaxy.kill_chain_order:
                print(f"New kill_chain_tactic found: {key}:{value}")
                technique_galaxy.kill_chain_order.append(tactic)
except (KeyError, FileNotFoundError):
    technique_galaxy = Galaxy({
        'description': galaxy_description,
        'icon': "map",
        'kill_chain_order': kill_chain_tactics,
        'name': technique_galaxy_name,
        'namespace': "mitre",
        'type': galaxy_type,
        'uuid': "c22c8c18-0ccd-4033-b2dd-804ad26af4b9",
        'version': 1
    })

technique_galaxy.save('mitre-fight-techniques')


#
# mitigations
#
mitigation_galaxy_name = "MITRE FiGHT Mitigations"
mitigation_cluster = Cluster({
    'authors': ["MITRE"],
    'category': 'mitigation',
    'name': mitigation_galaxy_name,
    'description': galaxy_description,
    'source': galaxy_source,
    'type': galaxy_type,
    'uuid': "fe20707f-2dfb-4436-8520-8fedb8c79668",
    'version': 1
})

for item in fight['mitigations']:
    element = {
        'value': item['name'].strip(),
        'description': item['description'].strip(),
        'uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), item['id'])),
        'meta': {
            'kill_chain': [],
            'refs': [f"https://fight.mitre.org/mitigations/{item['id']}"],
            'external_id': item['id']
        },
        'related': []
    }
    # rel to techniques
    for technique in item['techniques']:
        element['related'].append({
            'dest-uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), technique)),
            'type': 'mitigates'
        })
    mitigation_cluster.append(element, skip_duplicates=True)

mitigation_cluster.save('mitre-fight-mitigations')

for cluster, duplicate in mitigation_cluster.duplicates:
    print(f"Skipped duplicate: {duplicate} in cluster {cluster}")

try:
    mitigation_galaxy = Galaxy('mitre-fight-mitigations')
except (KeyError, FileNotFoundError):
    mitigation_galaxy = Galaxy({
        'description': galaxy_description,
        'icon': "shield-alt",
        'name': mitigation_galaxy_name,
        'namespace': "mitre",
        'type': galaxy_type,
        'uuid': "bcd85ca5-5ed7-4536-bca6-d16fb51adf55",
        'version': 1
    })

mitigation_galaxy.save('mitre-fight-mitigations')

#
# data sources / detections
#
detection_galaxy_name = "MITRE FiGHT Data Sources"
detection_cluster = Cluster({
    'authors': ["MITRE"],
    'category': 'data-source',
    'name': detection_galaxy_name,
    'description': galaxy_description,
    'source': galaxy_source,
    'type': galaxy_type,
    'uuid': "fb4410a1-5a39-4b30-934a-9cdfbcd4d2ad",
    'version': 1
})

for item in fight['data sources']:
    element = {
        'value': item['name'].strip(),
        'description': item['description'].strip(),
        'uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), item['id'])),
        'meta': {
            'kill_chain': [],
            'refs': [f"https://fight.mitre.org/data%sources/{item['id']}"],
            'external_id': item['id']
        },
        'related': []
    }
    # rel to techniques
    for technique in item['techniques']:
        element['related'].append({
            'dest-uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), technique)),
            'type': 'detects'
        })
    detection_cluster.append(element, skip_duplicates=True)

detection_cluster.save('mitre-fight-datasources')

for cluster, duplicate in detection_cluster.duplicates:
    print(f"Skipped duplicate: {duplicate} in cluster {cluster}")

try:
    detection_galaxy = Galaxy('mitre-fight-datasources')
except (KeyError, FileNotFoundError):
    detection_galaxy = Galaxy({
        'description': galaxy_description,
        'icon': "bell",
        'name': detection_galaxy_name,
        'namespace': "mitre",
        'type': galaxy_type,
        'uuid': "4ccc2400-55e4-42c2-bb8d-1d41883cef46",
        'version': 1
    })

detection_galaxy.save('mitre-fight-datasources')


print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh.")
