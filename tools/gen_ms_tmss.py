#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#    A simple convertor of the Threat Matrix for storage services to a MISP Galaxy datastructure.
#    Copyright (C) 2022 Christophe Vandeplas
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

import yaml
import os
import uuid
import re
import argparse
from pymispgalaxies import Cluster, Galaxy

parser = argparse.ArgumentParser(description='Create/update the Threat Matrix for storage services based on Markdown files.')
parser.add_argument("-p", "--path", required=True, help="Path of the 'Threat Matrix for storage services' git clone folder")

args = parser.parse_args()

if not os.path.exists(args.path):
    exit("ERROR: Threat Matrix for storage services folder incorrect")

with open(os.path.join(args.path, 'mkdocs.yml'), 'r') as f:
    mkdocs_data = yaml.load(f, Loader=yaml.BaseLoader)

tactics = []
clusters = {}


mitre_attack_pattern = Cluster('mitre-attack-pattern')


def find_mitre_uuid_from_technique_id(technique_id):
    try:
        return mitre_attack_pattern.get_by_external_id(technique_id).uuid
    except KeyError:
        print("No MITRE UUID found for technique_id: ", technique_id)
        return None


for nav_item in mkdocs_data['nav']:
    try:
        for tact_item in nav_item['Tactics']:
            try:
                tactic = next(iter(tact_item.keys()))
                tactics.append(tactic)
                for techn_items in tact_item[tactic]:
                    try:
                        # for techn_fname in techn_items['Techniques']:
                        for technique_name, fname in techn_items.items():
                            description_lst = []
                            with open(os.path.join(args.path, 'docs', fname), 'r') as technique_f:
                                # find the short description, residing between the main title (#) and next title (!!!) or table (|)
                                technique_f_lines = technique_f.read()
                                description = technique_f_lines.split('\n')[-2].strip()
                                technique_id = re.search(r'ID: (MS-T[0-9]+)', technique_f_lines).group(1)
                                try:
                                    # make relationship to MITRE ATT&CK
                                    mitre_technique_id = re.search(r'MITRE technique: \[(T[0-9]+)\]', technique_f_lines).group(1)
                                    mitre_technique_uuid = find_mitre_uuid_from_technique_id(mitre_technique_id)
                                    related = [
                                        {
                                            "dest-uuid": mitre_technique_uuid,
                                            "type": "related-to"
                                        }
                                    ]
                                except AttributeError:
                                    mitre_technique_uuid = None
                                    pass
                            # print(f"{tactic} / {technique} / {description}")
                            technique = f'{technique_id} - {technique_name}'
                            if technique not in clusters:
                                clusters[technique] = {
                                    'value': technique,
                                    'description': description,
                                    'uuid': str(uuid.uuid5(uuid.UUID("9319371e-2504-4128-8410-3741cebbcfd3"), technique)),
                                    'meta': {
                                        'kill_chain': [],
                                        'refs': [f"https://microsoft.github.io/Threat-matrix-for-storage-services/{fname[:-3]}"],
                                        'external_id': technique_id
                                    }
                                }
                                if mitre_technique_uuid:
                                    clusters[technique]['related'] = related
                            clusters[technique]['meta']['kill_chain'].append(f"TMSS-tactics:{tactic}")
                    except KeyError:
                        continue
                    except AttributeError:
                        continue
            except AttributeError:  # skip lines that have no field/value
                continue
        break
    except KeyError:
        continue

galaxy_type = "tmss"
galaxy_name = "Threat Matrix for storage services"
galaxy_description = 'Microsoft Defender for Cloud threat matrix for storage services contains attack tactics, techniques and mitigations relevant storage services delivered by cloud providers.'
galaxy_source = 'https://github.com/microsoft/Threat-matrix-for-storage-services'

try:
    galaxy = Galaxy('tmss')
except (KeyError, FileNotFoundError):
    galaxy = Galaxy({
        'icon': "map",
        'kill_chain_order': {
            'TMSS-tactics': tactics
        },
        'name': galaxy_name,
        'description': galaxy_description,
        'namespace': "microsoft",
        'type': galaxy_type,
        'uuid': "d6532b58-99e0-44a9-93c8-affe055e4443",
        'version': 1
    })

galaxy.save('tmss')

try:
    cluster = Cluster('tmss')
except (KeyError, FileNotFoundError):
    cluster = Cluster({
        'authors': ["Microsoft"],
        'category': 'tmss',
        'name': galaxy_name,
        'description': galaxy_description,
        'source': galaxy_source,
        'type': galaxy_type,
        'uuid': "aaf033a6-7f1e-45ab-beef-20a52b75b641",
        'version': 0
    })

# add authors based on the Acknowledgements page
authors = ('Evgeny Bogokovsky', 'Ram Pliskin')
for author in authors:
    cluster.authors.add(author)

for cluster_value in clusters.values():
    cluster.append(cluster_value)

cluster.save('tmss')

print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh, and update_README.")
