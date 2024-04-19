import os
import json
import argparse

thisDir = os.path.dirname(__file__)

clusters = []

pathClusters = os.path.join(thisDir, '../../clusters')
pathGalaxies = os.path.join(thisDir, '../../galaxies')

skip_list = ["cancer.json", "handicap.json", "ammunitions.json", "firearms.json"]

for f in os.listdir(pathGalaxies):
    if '.json' in f:
        with open(os.path.join(pathGalaxies, f), 'r') as f_in:
            galaxy_data = json.load(f_in)
            if galaxy_data.get('namespace') != 'deprecated':
                if f not in skip_list:
                    clusters.append(f)

clusters.sort()

for cluster in clusters:
    fullPathClusters = os.path.join(pathClusters, cluster)
    with open(fullPathClusters) as fp:
        c = json.load(fp)
    cluster_name = cluster.split(".")[0].upper()
    l = f'{cluster_name}'
    for v in c['values']:
        if 'uuid' not in v:
            continue
        l += f",{v['value']}"
        if 'meta' not in v:
            continue
        if 'synonyms' not in v['meta']:
            continue
        for synonym in v['meta']['synonyms']:
            l += f',{synonym}'
    print(l)

