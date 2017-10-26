#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Create a couple galaxy/cluster with cti\'s intrusion-sets\nMust be in the mitre/cti/ATTACK/intrusion-set folder')
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
            value['value'] = temp['name']
            value['meta'] = {}
            value['meta']['synonyms'] = temp['aliases']
            value['meta']['refs']= []
            for reference in temp['external_references']:
                if 'url' in reference:                    
                    value['meta']['refs'].append(reference['url'])
            value['meta']['uuid'] = re.search('--(.*)$', temp['id']).group(0)[2:]
            values.append(value)

galaxy = {}
galaxy['name'] = "Intrusion Set"
galaxy['type'] = "mitre-intrusion-set"
galaxy['description'] = "Name of ATT&CK Group"
galaxy['uuid' ] = "1023f364-7831-11e7-8318-43b5531983ab"
galaxy['version'] = args.version
galaxy['icon'] = "user-secret"

cluster = {} 
cluster['name'] = "intrusion Set"
cluster['type'] = "mitre-intrusion-set"
cluster['description'] = "Name of ATT&CK Group"
cluster['version'] = args.version
cluster['source'] = "https://github.com/mitre/cti"
cluster['uuid' ] = "10df003c-7831-11e7-bdb9-971cdd1218df"
cluster['authors'] = ["MITRE"]
cluster['values'] = values

with open('generate/galaxies/mitre_intrusion-set.json', 'w') as galaxy_file:
    json.dump(galaxy, galaxy_file, indent=4)

with open('generate/clusters/mitre_intrusion-set.json', 'w') as cluster_file:
    json.dump(cluster, cluster_file, indent=4)
