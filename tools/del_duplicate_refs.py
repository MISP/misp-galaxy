#!/usr/bin/env python3
# coding=utf-8
"""
    Tool to remove duplicates in cluster references
"""
import sys
import json

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

for c in data['values']:
    c['meta']['refs'] = list(dict.fromkeys(c['meta']['refs']))

with open(sys.argv[1], 'w') as f:
    json.dump(data, f)

