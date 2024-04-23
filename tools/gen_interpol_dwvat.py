#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#    A simple convertor of the Interpol Dark Web and Virtual Assets Taxonomies to a MISP Galaxy datastructure.
#    https://github.com/INTERPOL-Innovation-Centre/DW-VA-Taxonomy
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

import yaml
import os
import uuid
import re
import json

import argparse

parser = argparse.ArgumentParser(description='Create/update the Interpol Dark Web and Virtual Assets Taxonomies based on Markdown files.')
parser.add_argument("-p", "--path", required=True, help="Path of the 'DW-VA-Taxonomy' git clone folder")

args = parser.parse_args()

if not os.path.exists(args.path):
    exit("ERROR: DW-VA-Taxonomy folder incorrect")

'''
contains _data folder with
- abuses.yaml - simple taxonomy
- entities.yaml - matrix like taxonomy
'''

try:
    with open(os.path.join('..', 'galaxies', 'interpol-dwva.json'), 'r') as f:
        json_galaxy = json.load(f)

except FileNotFoundError:
    json_galaxy = {
        'icon': "user-secret",
        'kill_chain_order': {
            'Entities': [],
            'Abuses': ['Concept']
        },
        'name': "INTERPOL DWVA Taxonomy",
        'description': "This taxonomy defines common forms of abuses and entities that represent real-world actors and service that are part of a larger Darknet- and Cryptoasset Ecosystems.",
        'namespace': "interpol",
        'type': "dwva",
        'uuid': "a375d7fd-0a3e-41cf-a531-ef56033df967",
        'version': 1
    }

try:
    with open(os.path.join('..', 'clusters', 'interpol-dwva.json'), 'r') as f:
        json_cluster = json.load(f)
except FileNotFoundError:
    json_cluster = {
        'authors': ["INTERPOL Darkweb and Virtual Assets Working Group"],
        'category': 'dwva',
        'name': "INTERPOL DWVA Taxonomy",
        'description': "This taxonomy defines common forms of abuses and entities that represent real-world actors and service that are part of a larger Darknet- and Cryptoasset Ecosystems.",
        'source': 'https://interpol-innovation-centre.github.io/DW-VA-Taxonomy/',
        'type': "dwva",
        'uuid': "b15898ba-a923-4916-856c-0dfe8b174196",
        'values': [],
        'version': 1
    }


tactics = set()
clusters_dict = {}
# FIXME create dict for the existing clusters, so we can update the clusters without losing the relations

#
# Entities
#
with open(os.path.join(args.path, '_data', 'entities.yaml'), 'r') as f:
    entities_data = yaml.safe_load(f)

# build a broader concept list so we can ignore them later on
broaders = set()
for section in entities_data:
    try:
        broaders.add(entities_data[section]['broader'])
    except KeyError:
        pass
# the Entities
for section in entities_data:
    item = entities_data[section]
    if item['type'] == 'concept':
        if item['id'] in broaders:  # skip the broader concepts
            continue
        if 'broader' not in item:
            item['broader'] = 'generic'
        tactics.add(item['broader'].title())
        value = item['prefLabel']
        clusters_dict[value] = {
            'value': value,
            'description': item['description'],
            'uuid': str(uuid.uuid5(uuid.UUID("d0ceebc2-877b-4873-9785-d00f279ccb45"), value)),
            'meta': {
                'kill_chain': [f"Entities:{item['broader'].title()}"],
            }
        }
        try:
            clusters_dict[value]['meta']['refs'] = [item['seeAlso']]
        except KeyError:
            pass

#
# Abuses
#
with open(os.path.join(args.path, '_data', 'abuses.yaml'), 'r') as f:
    entities_data = yaml.safe_load(f)
for section in entities_data:
    item = entities_data[section]
    if item['type'] == 'concept':
        value = item['prefLabel']
        clusters_dict[value] = {
            'value': value,
            'description': item['description'],
            'uuid': str(uuid.uuid5(uuid.UUID("d0ceebc2-877b-4873-9785-d00f279ccb45"), value)),
            'meta': {
                'kill_chain': [f"Abuses:Concept"],
            }
        }
        try:
            clusters_dict[value]['meta']['refs'] = [item['seeAlso']]
        except KeyError:
            pass


#
# Finally transform dict to list
#
clusters = []
for item in clusters_dict.values():
    clusters.append(item)

json_cluster['values'] = clusters
json_galaxy['kill_chain_order']['Entities'] = sorted(list(tactics))

# save the Galaxy and Cluster file
with open(os.path.join('..', 'galaxies', 'interpol-dwva.json'), 'w') as f:
    json.dump(json_galaxy, f, indent=2, sort_keys=True, ensure_ascii=False)
    f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things


with open(os.path.join('..', 'clusters', 'interpol-dwva.json'), 'w') as f:
    json.dump(json_cluster, f, indent=2, sort_keys=True, ensure_ascii=False)
    f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things

print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh.")
