#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Create a couple galaxy/cluster with cti\'s attack-patterns\nMust be in the mitre/cti/ATTACK/attack-pattern folder')
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
            value['meta']['refs'] = []
            for reference in temp['external_references']:
                if 'url' in reference:                    
                    value['meta']['refs'].append(reference['url'])
            if 'x_mitre_data_sources' in temp:
                value['meta']['mitre_data_sources'] = temp['x_mitre_data_sources']
            if 'x_mitre_platforms' in temp:
                value['meta']['mitre_platforms'] = temp['x_mitre_platforms']
            values.append(value)
            value['meta']['uuid'] = re.search('--(.*)$', temp['id']).group(0)[2:]

galaxy = {}
galaxy['name'] = "Attack Pattern"
galaxy['type'] = "mitre-attack-pattern"
galaxy['description'] = "ATT&CK Tactic"
galaxy['uuid' ] = "c4e851fa-775f-11e7-8163-b774922098cd"
galaxy['version'] = args.version
galaxy['icon'] = "map"

cluster = {} 
cluster['name'] = "Attack Pattern"
cluster['type'] = "mitre-attack-pattern"
cluster['description'] = "ATT&CK tactic"
cluster['version'] = args.version
cluster['source'] = "https://github.com/mitre/cti"
cluster['uuid' ] = "dcb864dc-775f-11e7-9fbb-1f41b4996683"
cluster['authors'] = ["MITRE"]
cluster['values'] = values

with open('generate/galaxies/mitre_attack-pattern.json', 'w') as galaxy_file:
    json.dump(galaxy, galaxy_file, indent=4)

with open('generate/clusters/mitre_attack-pattern.json', 'w') as cluster_file:
    json.dump(cluster, cluster_file, indent=4)
