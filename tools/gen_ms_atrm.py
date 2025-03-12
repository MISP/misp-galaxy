#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#    A simple convertor of the Azure-Threat-Research-Matrix to a MISP Galaxy datastructure.
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


parser = argparse.ArgumentParser(description='Create/update the Azure Threat Research Matrix based on Markdown files.')
parser.add_argument("-p", "--path", required=True, help="Path of the 'Azure Threat Research Matrix' git clone folder")

args = parser.parse_args()

if not os.path.exists(args.path):
    exit("ERROR: Azure Threat Research Matrix folder incorrect")

with open(os.path.join(args.path, 'mkdocs.yml'), 'r') as f:
    mkdocs_data = yaml.load(f, Loader=yaml.BaseLoader)

tactics = []
clusters = {}

for nav_item in mkdocs_data['nav']:
    try:
        for tact_item in nav_item['Tactics']:
            tactic = next(iter(tact_item.keys()))
            tactics.append(tactic)
            for techn_items in tact_item[tactic]:
                try:
                    for techn_fname in techn_items['Techniques']:
                        for technique, fname in techn_fname.items():
                            description_lst = []
                            with open(os.path.join(args.path, 'docs', fname), 'r') as technique_f:
                                # find the short description, residing between the main title (#) and next title (!!!) or table (|)
                                for line in technique_f:
                                    if line.startswith('#'):
                                        continue
                                    if line.startswith('!!!') or line.startswith('|'):
                                        break
                                    description_lst.append(line.strip())
                            description = ''.join(description_lst)
                            # print(f"{tactic} / {technique} / {description}")
                            if technique not in clusters:
                                clusters[technique] = {
                                    'value': technique,
                                    'description': description,
                                    'uuid': str(uuid.uuid5(uuid.UUID("9319371e-2504-4128-8410-3741cebbcfd3"), technique)),
                                    'meta': {
                                        'kill_chain': [],
                                        'refs': [f"https://microsoft.github.io/Azure-Threat-Research-Matrix/{fname[:-3]}"],
                                        'external_id': technique.split(' ')[0]
                                    }
                                }
                            else:
                                pass
                            clusters[technique]['meta']['kill_chain'].append(f"ATRM-tactics:{tactic}")
                except KeyError:
                    continue
        break
    except KeyError:
        continue


try:
    cluster = Cluster('atrm')
except (KeyError, FileNotFoundError):
    cluster = Cluster({
        'authors': ["Microsoft"],
        'category': 'atrm',
        'name': "Azure Threat Research Matrix",
        'description': "The purpose of the Azure Threat Research Matrix (ATRM) is to educate readers on the potential of Azure-based tactics, techniques, and procedures (TTPs). It is not to teach how to weaponize or specifically abuse them. For this reason, some specific commands will be obfuscated or parts will be omitted to prevent abuse.",
        'source': 'https://github.com/microsoft/Azure-Threat-Research-Matrix',
        'type': "atrm",
        'uuid': "b541a056-154c-41e7-8a56-41db3f871c00",
        'version': 0
    })

# add authors based on the Acknowledgements page
with open(os.path.join(args.path, 'docs', 'acknowledgments.md'), 'r') as f:
    for line in f:
        if line.startswith('* '):
            try:
                cluster.authors.add(re.search(r'\w+ [\w&]+', line).group())
            except AttributeError:
                cluster.authors.add(re.search(r'\w+', line).group())

for cluster_value in clusters.values():
    cluster.append(cluster_value)

cluster.save('atrm')


try:
    galaxy = Galaxy('atrm')
except (KeyError, FileNotFoundError):
    galaxy = Galaxy({
        'icon': "map",
        'kill_chain_order': {
            'ATRM-tactics': tactics
        },
        'name': "Azure Threat Research Matrix",
        'description': "The purpose of the Azure Threat Research Matrix (ATRM) is to educate readers on the potential of Azure-based tactics, techniques, and procedures (TTPs). It is not to teach how to weaponize or specifically abuse them. For this reason, some specific commands will be obfuscated or parts will be omitted to prevent abuse.",
        'namespace': "microsoft",
        'type': "atrm",
        'uuid': "b541a056-154c-41e7-8a56-41db3f871c00",
        'version': 1
    })

galaxy.save('atrm')

print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh, and also update_README_with_index.py.")
