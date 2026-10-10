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
    print(f)
    with open(os.path.join(pathClusters, f), encoding='utf-8') as fr:
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
readme_marker_start = '# Available Galaxy - clusters'
readme_marker_end = '# Online documentation'
with open('../README.md', 'r', encoding='utf-8') as f:
    readme_lines = f.readlines()

# Locate both markers up front. The generated index replaces everything
# between them, so if either is missing -- renamed heading, reordered
# README -- the rebuild would silently truncate the file from the start
# marker onwards. Refuse to write instead.
start_idx = end_idx = None
for i, line in enumerate(readme_lines):
    stripped = line.strip()
    if stripped == readme_marker_start and start_idx is None:
        start_idx = i
    elif stripped == readme_marker_end and start_idx is not None:
        end_idx = i
        break

if start_idx is None or end_idx is None:
    missing = readme_marker_start if start_idx is None else readme_marker_end
    raise SystemExit(
        f"ERROR: marker {missing!r} not found in ../README.md (start={start_idx}, "
        f"end={end_idx}). README.md left unchanged -- the index is inserted "
        f"between {readme_marker_start!r} and {readme_marker_end!r}, so both "
        f"headings must be present, in that order."
    )

readme_out = readme_lines[:start_idx + 1]
readme_out.append("\n")
readme_out += output
readme_out.append("\n")
readme_out += readme_lines[end_idx:]

with open('../README.md', 'w', encoding='utf-8') as f:
    f.write(''.join(readme_out))

print("README.md updated with the index of the galaxies.")
