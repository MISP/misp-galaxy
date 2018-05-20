#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Create a couple galaxy/cluster with cti\'s attack-patterns\nMust be in the mitre/cti/pre-attack/attack-pattern folder')
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
            value['meta']['refs'] = []
            for reference in temp['external_references']:
                if 'url' in reference and reference['url'] not in value['meta']['refs']:
                    value['meta']['refs'].append(reference['url'])
                if 'external_id' in reference:
                    value['meta']['external_id'] = reference['external_id']
            value['meta']['kill_chain'] = []
            for killchain in temp['kill_chain_phases']:
                value['meta']['kill_chain'].append(killchain['kill_chain_name'] + ':pre-attack:' + killchain['phase_name'])
            if 'x_mitre_data_sources' in temp:
                value['meta']['mitre_data_sources'] = temp['x_mitre_data_sources']
            if 'x_mitre_platforms' in temp:
                value['meta']['mitre_platforms'] = temp['x_mitre_platforms']
            values.append(value)
            value['uuid'] = re.search('--(.*)$', temp['id']).group(0)[2:]

galaxy = {}
galaxy['name'] = "Pre Attack - Attack Pattern"
galaxy['type'] = "mitre-pre-attack-attack-pattern"
galaxy['description'] = "ATT&CK Tactic"
galaxy['uuid' ] = "1f665850-1708-11e8-9cfe-4792b2a91402"
galaxy['version'] = args.version
galaxy['icon'] = "map"
galaxy['namespace'] = "mitre-attack"

cluster = {}
cluster['name'] = "Pre Attack - Attack Pattern"
cluster['type'] = "mitre-pre-attack-attack-pattern"
cluster['description'] = "ATT&CK tactic"
cluster['version'] = args.version
cluster['source'] = "https://github.com/mitre/cti"
cluster['uuid' ] = "03c13bec-1708-11e8-92a0-a747c0787089"
cluster['authors'] = ["MITRE"]
cluster['values'] = values

with open('generate/galaxies/mitre-pre-attack-attack-pattern.json', 'w') as galaxy_file:
    json.dump(galaxy, galaxy_file, indent=4)

with open('generate/clusters/mitre-pre-attack-attack-pattern.json', 'w') as cluster_file:
    json.dump(cluster, cluster_file, indent=4)
