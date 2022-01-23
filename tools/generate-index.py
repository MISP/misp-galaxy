#!/usr/bin/env python3
import json
import os
import argparse


parser = argparse.ArgumentParser(description='Generate a markdown index with all the galaxy available')
parser.add_argument("-v", "--verbose", action='store_true', help='Verbose output')
args = parser.parse_args()


def gen_galaxy_tag(galaxy_name, cluster_name):
    # return 'misp-galaxy:{}="{}"'.format(galaxy_name, cluster_name)
    return '{}={}'.format(galaxy_name, cluster_name)

galaxies_fnames = []
files_to_ignore = []
pathClusters = '../clusters'

for f in os.listdir(pathClusters):
    if '.json' in f and f not in files_to_ignore:
        galaxies_fnames.append(f)

galaxies_fnames.sort()
output = ""

for f in galaxies_fnames:
    with open(os.path.join(pathClusters, f)) as fr:
        cluster = json.load(fr)
    output = f'{output}\n## {cluster["name"]}\n\n'
    link = cluster["name"].replace(" ", "_").lower()
    total = len(cluster["values"])
    output = f'{output}[{cluster["name"]}](https://www.misp-project.org/galaxy.html#_{link}) - {cluster["description"]}\n'
    output = f'{output}\nCategory: *{cluster["category"]}* - source: *{cluster["source"]}* - total: *{total}* elements\n'
    output = f'{output}\n[[HTML](https://www.misp-project.org/galaxy.html#_{link})] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/{f})]\n'

print(output)
