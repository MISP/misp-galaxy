#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Create a couple galaxy/cluster with cti\'s courses-of-action.\nMust be in the mitre/cti/mobile-attack/course-of-action folder')
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
            value['uuid'] = re.search('--(.*)$', temp['id']).group(0)[2:]
            value['meta'] = {}
            value['meta']['external_id'] = temp['external_references'][0]['external_id']                
            values.append(value)

galaxy = {}
galaxy['name'] = "Mobile Attack - Course of Action"
galaxy['type'] = "mitre-mobile-attack-course-of-action"
galaxy['description'] = "ATT&CK Mitigation"
galaxy['uuid' ] = "0282356a-1708-11e8-8f53-975633d5c03c"
galaxy['version'] = args.version
galaxy['icon'] = "chain"
galaxy['namespace'] = "mitre-attack"

cluster = {}
cluster['name'] = "Mobile Attack - Course of Action"
cluster['type'] = "mitre-mobile-attack-course-of-action"
cluster['description'] = "ATT&CK Mitigation"
cluster['version'] = args.version
cluster['source'] = "https://github.com/mitre/cti"
cluster['uuid' ] = "03956f9e-1708-11e8-8395-976b24233e15"
cluster['authors'] = ["MITRE"]
cluster['values'] = values

with open('generate/galaxies/mitre-mobile-attack-course-of-action.json', 'w') as galaxy_file:
    json.dump(galaxy, galaxy_file, indent=4)

with open('generate/clusters/mitre-mobile-attack-course-of-action.json', 'w') as cluster_file:
    json.dump(cluster, cluster_file, indent=4)
