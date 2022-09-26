#!/usr/bin/env python3
# coding=utf-8
"""
    Tool to remove duplicates in cluster references
"""
import sys
import json

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

unique_uuid = set()
values = []
for c in data['values']:
    if c['uuid'] in unique_uuid:
        sys.stderr.write(f"Duplicate UUID - {c['uuid']}\n")
        continue
    unique_uuid.add(c['uuid'])
    values.append(c)

data['values'] = []
data['values'] = values

with open(sys.argv[1], 'w') as f:
    json.dump(data, f)

