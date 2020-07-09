#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
import uuid
import re

parser = argparse.ArgumentParser(description='Sort ransomnotes.')
parser.add_argument("-f", "--filename", required=True, help="name of the cluster")
args = parser.parse_args()

if 'mitre-' in args.filename:
    exit()

with open(args.filename) as json_file:
    data = json.load(json_file)
    json_file.close()
    
    new_file = {}
    for key in data:
        if key != 'values': 
            new_file[key]=data[key]
        else:
            new_file['values']=[]
            values = data[key]
            for ransomware in values:
                ransom_cluster= {}
                for attribute in ransomware:
                    if attribute != 'meta':
                        ransom_cluster[attribute]=ransomware[attribute]
                    else:
                        ransom_cluster['meta']={}
                        meta = ransomware['meta']
                        for metadata in meta:
                            if metadata != 'ransomnotes':
                                ransom_cluster['meta'][metadata]=meta[metadata]
                            else:
                                for ransomnote in meta['ransomnotes']:
                                    if ransomnote.startswith('http'):
                                        if not ransom_cluster['meta'].get('ransomnotes-refs'):
                                            ransom_cluster['meta']['ransomnotes-refs']=[]
                                        ransom_cluster['meta']['ransomnotes-refs'].append(ransomnote)
                                    elif re.search('\.([a-zA-Z0-9]){3,4}$',ransomnote):
                                        if not ransom_cluster['meta'].get('ransomnotes-filenames'):
                                            ransom_cluster['meta']['ransomnotes-filenames']=[]
                                        ransom_cluster['meta']['ransomnotes-filenames'].append(ransomnote)
                                    else:
                                        if not ransom_cluster['meta'].get('ransomnotes'):
                                            ransom_cluster['meta']['ransomnotes']=[]
                                        ransom_cluster['meta']['ransomnotes'].append(ransomnote)
                new_file['values'].append(ransom_cluster)
                
with open('ransom2.json', 'w') as json_file:
    json.dump(new_file, json_file, indent=2, sort_keys=True, ensure_ascii=False)

