#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Create a couple galaxy/cluster with cti\'s tools\nMust be in the mitre/cti/enterprise-attack/tool folder')
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
galaxy['name'] = "Enterprise Attack - Tool"
galaxy['type'] = "mitre-enterprise-attack-tool"
galaxy['description'] = "Name of ATT&CK software"
galaxy['uuid' ] = "fbfa0470-1707-11e8-be22-eb46b373fdd3"
galaxy['version'] = args.version
galaxy['icon'] = "gavel"

cluster = {}
cluster['name'] = "Enterprise Attack - Tool"
cluster['type'] = "mitre-enterprise-attack-tool"
cluster['description'] = "Name of ATT&CK software"
cluster['version'] = args.version
cluster['source'] = "https://github.com/mitre/cti"
cluster['uuid' ] = "fc1ea6e0-1707-11e8-ac05-2b70d00c354e"
cluster['authors'] = ["MITRE"]
cluster['values'] = values

with open('generate/galaxies/mitre-enterprise-attack-tool.json', 'w') as galaxy_file:
    json.dump(galaxy, galaxy_file, indent=4)

with open('generate/clusters/mitre-enterprise-attack-tool.json', 'w') as cluster_file:
    json.dump(cluster, cluster_file, indent=4)
