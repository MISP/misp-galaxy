#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import argparse
import uuid

parser = argparse.ArgumentParser(description='Add missing uuids in clusters')
parser.add_argument("-f", "--filename", required=True, help="nameof the cluster (without .json)")
args = parser.parse_args()

with open(args.filename+'.json') as json_file:
    data = json.load(json_file)
    json_file.close()

    for value in data['values']:
        if 'uuid' not in value:
            value['uuid'] = str(uuid.uuid4())

with open(args.filename+'.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)
