#!/usr/bin/env python3
# coding=utf-8
"""
    Tool to remove duplicates in value
"""
import sys
import json

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

#for c in data['values']:
#    c['value'] = f'{c["value"]} - {c["meta"]["description"]}'

value_seen = []
data_output = []
for c in data['values']:
    if c['value'] in value_seen:
        continue
    else:
        data_output.append(c)
        value_seen.append(c['value'])

data['values'] = data_output
with open(sys.argv[1], 'w') as f:
    json.dump(data, f)

