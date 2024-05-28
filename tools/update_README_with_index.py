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
files_to_ignore = ["cancer.json", "handicap.json"]
pathClusters = '../clusters'
pathGalaxies = '../galaxies'

for f in os.listdir(pathClusters):
    if '.json' in f and f not in files_to_ignore:
        galaxies_fnames.append(f)

galaxies_fnames.sort()
output = []

# generate the index
for f in galaxies_fnames:
    with open(os.path.join(pathClusters, f)) as fr:
        cluster = json.load(fr)
    with open(os.path.join(pathGalaxies, f)) as fr:
        galaxy = json.load(fr)
    if galaxy.get('namespace') == 'deprecated':
        continue
    output.append(f"## {cluster['name']}\n\n")
    link = f.split('.')[0]
    total = len(cluster['values'])
    output.append(f"[{cluster['name']}](https://www.misp-galaxy.org/{link}) - {cluster['description']}\n")
    output.append(f"\nCategory: *{cluster['category']}* - source: *{cluster['source']}* - total: *{total}* elements\n")
    output.append(f"\n[[HTML](https://www.misp-galaxy.org/{link})] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/{f})]\n\n")

# update the README.md
readme_out = []
readme_marker_start = '# Available Galaxy - clusters'
readme_marker_end = '# Online documentation'
with open('../README.md', 'r') as f:
    skip = False
    for line in f:
        if not skip:
            readme_out.append(line)
        if line.strip() == readme_marker_start:
            skip = True
        if line.strip() == readme_marker_end:
            # append the index
            readme_out.append("\n")
            readme_out += output
            readme_out.append("\n")
            readme_out.append(line)
            # stop skipping
            skip = False


with open('../README.md', 'w') as f:
    f.write(''.join(readme_out))

print("README.md updated with the index of the galaxies.")
