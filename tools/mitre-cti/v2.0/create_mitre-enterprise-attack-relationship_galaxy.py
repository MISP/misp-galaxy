#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Create a couple galaxy/cluster with cti\'s relationship\nMust be in the mitre/cti/enterprise-attack/relationship folder')
parser.add_argument("-v", "--version", type=int, required=True, help="Version of the galaxy. Please increment the previous one")
args = parser.parse_args()

values = []

path = "relationship/"
for element in os.listdir(path):
    with open(path+element) as json_data:
        d = json.load(json_data)
        json_data.close()

    temp = d['objects'][0]
    source = temp['source_ref']
    target = temp['target_ref']
    relationship = temp['relationship_type']

    if source.startswith('attack-pattern'):
        paths = "attack-pattern/"
    elif source.startswith('course-of-action'):
        paths = "course-of-action/"
    elif source.startswith('identity'):
        paths = "identity/"
    elif source.startswith('intrusion-set'):
        paths = "intrusion-set/"
    elif source.startswith('malware'):
        paths = "malware/"
    elif source.startswith('marking-definition'):
        paths = "marking-definition/"
    elif source.startswith('tool'):
        paths = "tool/"
    else:
        print('Invalid value')
        continue

    with open(paths+source+'.json') as json_data:
        s = json.load(json_data)
        json_data.close()

    if target.startswith('attack-pattern'):
        patht = "attack-pattern/"
    elif target.startswith('course-of-action'):
        patht = "course-of-action/"
    elif target.startswith('identity'):
        patht = "identity/"
    elif target.startswith('intrusion-set'):
        patht = "intrusion-set/"
    elif target.startswith('malware'):
        patht = "malware/"
    elif target.startswith('marking-definition'):
        patht = "marking-definition/"
    elif target.startswith('tool'):
        patht = "tool/"
    else:
        print('Invalid value')
        continue

    with open(patht+target+'.json') as json_data:
        t = json.load(json_data)
        json_data.close()

    value = {}
    value['meta'] = {}
    value['uuid'] = re.search('--(.*)$', temp['id']).group(0)[2:]
    value['meta']['source-uuid'] = re.search('--(.*)$', s['objects'][0]['id']).group(0)[2:]
    value['meta']['target-uuid'] = re.search('--(.*)$', t['objects'][0]['id']).group(0)[2:]
    value['value'] = s['objects'][0]['name'] + ' (' + s['objects'][0]['external_references'][0]['external_id'] + ') ' + relationship + ' ' + t['objects'][0]['name'] + ' (' + t['objects'][0]['external_references'][0]['external_id'] + ')'
    # value['value'] = s['objects'][0]['name'] + ' ' + relationship + ' ' + t['objects'][0]['name']
    values.append(value)

galaxy = {}
galaxy['name'] = "Enterprise Attack - Relationship"
galaxy['type'] = "mitre-enterprise-attack-relationship"
galaxy['description'] = "Mitre Relationship"
galaxy['uuid' ] = "fc404638-1707-11e8-a5cf-b78b9b562766"
galaxy['version'] = args.version
galaxy['icon'] = "link"

cluster = {}
cluster['name'] = "Enterprise Attack - Relationship"
cluster['type'] = "mitre-enterprise-attack-relationship"
cluster['description'] = "MITRE Relationship"
cluster['version'] = args.version
cluster['source'] = "https://github.com/mitre/cti"
cluster['uuid' ] = "fc605f90-1707-11e8-9d6a-9f165ac2ab5c"
cluster['authors'] = ["MITRE"]
cluster['values'] = values

with open('generate/galaxies/mitre-enterprise-attack-relationship.json', 'w') as galaxy_file:
    json.dump(galaxy, galaxy_file, indent=4)

with open('generate/clusters/mitre-enterprise-attack-relationship.json', 'w') as cluster_file:
    json.dump(cluster, cluster_file, indent=4)
