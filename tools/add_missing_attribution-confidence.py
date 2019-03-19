#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
import uuid

parser = argparse.ArgumentParser(description='Add missing attribution-confidence in threat-actor clusters')
parser.add_argument("-f", "--filename", required=True, help="name of the cluster")
args = parser.parse_args()

with open(args.filename) as json_file:
    data = json.load(json_file)
    json_file.close()

    for value in data['values']:
        if value.get('meta'):
            if not value.get('meta').get('attribution-confidence') and (value.get('meta').get('cfr-suspected-state-sponsor') or value.get('meta').get('country')):
                value.set('meta')['attribution-confidence'] = "50"
            elif value.get('meta').get('attribution-confidence')  and (value.get('meta').get('cfr-suspected-state-sponsor') or value.get('meta').get('country')):
                value.get('meta')['attribution-confidence'] = str(value.get('meta').get('attribution-confidence'))



with open(args.filename, 'w') as json_file:
    json.dump(data, json_file, indent=2, sort_keys=True, ensure_ascii=False)
