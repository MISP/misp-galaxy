#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
import uuid

parser = argparse.ArgumentParser(description='Add missing uuids in clusters')
parser.add_argument("-f", "--filename", required=True, help="name of the cluster")
args = parser.parse_args()

if 'mitre-' in args.filename:
    exit()

with open(args.filename) as json_file:
    data = json.load(json_file)
    json_file.close()

    for value in data['values']:
        if not value.get('uuid'):
            value['uuid'] = str(uuid.uuid4())

with open(args.filename, 'w') as json_file:
    json.dump(data, json_file, indent=2, sort_keys=True, ensure_ascii=False)
