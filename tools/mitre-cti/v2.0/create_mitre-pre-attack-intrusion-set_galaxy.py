#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Create a couple galaxy/cluster with cti\'s intrusion-sets\nMust be in the mitre/cti/pre-attack/intrusion-set folder')
parser.add_argument("-v", "--version", type=int, required=True, help="Version of the galaxy. Please increment the previous one")
args = parser.parse_args()

values = []

for element in os.listdir('.'):
    if element.endswith('.json'):
        with open(element) as json_data:
            d = json.load(json_data)
            json_data.close()

            temp = d['objects'][0]

            value = {}
            value['description'] = temp['description']
            value['value'] = temp['name'] + ' - ' + temp['external_references'][0]['external_id']
            value['meta'] = {}
            value['meta']['synonyms'] = temp['aliases']
            value['meta']['refs']= []
            for reference in temp['external_references']:
                if 'url' in reference and reference['url'] not in value['meta']['refs']:
                    value['meta']['refs'].append(reference['url'])
                if 'external_id' in reference:
                    value['meta']['external_id'] = reference['external_id']                    
            value['uuid'] = re.search('--(.*)$', temp['id']).group(0)[2:]
            values.append(value)

galaxy = {}
galaxy['name'] = "Pre Attack - Intrusion Set"
galaxy['type'] = "mitre-pre-attack-intrusion-set"
galaxy['description'] = "Name of ATT&CK Group"
galaxy['uuid' ] = "1fb6d5b4-1708-11e8-9836-8bbc8ce6866e"
galaxy['version'] = args.version
galaxy['icon'] = "user-secret"
galaxy['namespace'] = "mitre-attack"

cluster = {}
cluster['name'] = "Pre Attack - intrusion Set"
cluster['type'] = "mitre-pre-attack-intrusion-set"
cluster['description'] = "Name of ATT&CK Group"
cluster['version'] = args.version
cluster['source'] = "https://github.com/mitre/cti"
cluster['uuid' ] = "1fdc8fa2-1708-11e8-99a3-67b4efc13c4f"
cluster['authors'] = ["MITRE"]
cluster['values'] = values

with open('generate/galaxies/mitre-pre-attack-intrusion-set.json', 'w') as galaxy_file:
    json.dump(galaxy, galaxy_file, indent=4)

with open('generate/clusters/mitre-pre-attack-intrusion-set.json', 'w') as cluster_file:
    json.dump(cluster, cluster_file, indent=4)
