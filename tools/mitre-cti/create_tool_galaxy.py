#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Create a couple galaxy/cluster with cti\'s tools\nMust be in the mitre/cti/ATTACK/tool folder')
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
            if'x_mitre_aliases' in temp:
                value['meta']['synonyms'] = temp['x_mitre_aliases']     
            value['meta']['uuid'] = re.search('--(.*)$', temp['id']).group(0)[2:]
            values.append(value)

galaxy = {}
galaxy['name'] = "Tool"
galaxy['type'] = "mitre-tool"
galaxy['description'] = "Name of ATT&CK software"
galaxy['uuid' ] = "d5cbd1a2-78f6-11e7-a833-7b9bccca9649"
galaxy['version'] = args.version
galaxy['icon'] = "gavel"

cluster = {} 
cluster['name'] = "Tool"
cluster['type'] = "mitre-tool"
cluster['description'] = "Name of ATT&CK software"
cluster['version'] = args.version
cluster['source'] = "https://github.com/mitre/cti"
cluster['uuid' ] = "d700dc5c-78f6-11e7-a476-5f748c8e4fe0"
cluster['authors'] = ["MITRE"]
cluster['values'] = values

with open('generate/galaxies/mitre_tool.json', 'w') as galaxy_file:
    json.dump(galaxy, galaxy_file, indent=4)

with open('generate/clusters/mitre_tool.json', 'w') as cluster_file:
    json.dump(cluster, cluster_file, indent=4)
