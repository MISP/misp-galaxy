#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Create a couple galaxy/cluster with cti\'s tools\nMust be in the mitre/cti/mobile-attack/tool folder')
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
            if'x_mitre_aliases' in temp:
                value['meta']['synonyms'] = temp['x_mitre_aliases']
            value['uuid'] = re.search('--(.*)$', temp['id']).group(0)[2:]
            values.append(value)

galaxy = {}
galaxy['name'] = "Mobile Attack - Tool"
galaxy['type'] = "mitre-mobile-attack-tool"
galaxy['description'] = "Name of ATT&CK software"
galaxy['uuid' ] = "1d0b4bce-1708-11e8-9e6e-1b130c9b0a91"
galaxy['version'] = args.version
galaxy['icon'] = "gavel"
galaxy['namespace'] = "mitre-attack"

cluster = {}
cluster['name'] = "Mobile Attack - Tool"
cluster['type'] = "mitre-mobile-attack-tool"
cluster['description'] = "Name of ATT&CK software"
cluster['version'] = args.version
cluster['source'] = "https://github.com/mitre/cti"
cluster['uuid' ] = "02cee87e-1708-11e8-8f15-8b33e4d6194b"
cluster['authors'] = ["MITRE"]
cluster['values'] = values

with open('generate/galaxies/mitre-mobile-attack-tool.json', 'w') as galaxy_file:
    json.dump(galaxy, galaxy_file, indent=4)

with open('generate/clusters/mitre-mobile-attack-tool.json', 'w') as cluster_file:
    json.dump(cluster, cluster_file, indent=4)
