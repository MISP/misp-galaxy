#!/usr/bin/python

import json
import os

pathClusters = '../../clusters'
pathSite = './site/docs'

galaxies_fnames = []
files_to_ignore = [] # if you want to skip a specific cluster in the generation

for f in os.listdir(pathClusters):
    if '.json' in f and f not in files_to_ignore:
        galaxies_fnames.append(f)

galaxies_fnames.sort()

index_output = ""
index_output += """
# MISP Galaxy

The MISP galaxy offers a streamlined approach for representing large entities, known as clusters, which can be linked to MISP events or attributes. Each cluster consists of one or more elements, represented as key-value pairs. MISP galaxy comes with a default knowledge base, encompassing areas like Threat Actors, Tools, Ransomware, and ATT&CK matrices. However, users have the flexibility to modify, update, replace, or share these elements according to their needs.

Clusters and vocabularies within MISP galaxy can be utilized in their original form or as a foundational knowledge base. The distribution settings for each cluster can be adjusted, allowing for either restricted or wide dissemination.

Additionally, MISP galaxies enable the representation of existing standards like the MITRE ATT&CK™ framework, as well as custom matrices.

The aim is to provide a core set of clusters for organizations embarking on analysis, which can be further tailored to include localized, private information or additional, shareable data.

Clusters serve as an open and freely accessible knowledge base, which can be utilized and expanded within [MISP](https://www.misp-project.org/) or other threat intelligence platforms.

## Publicly available clusters

"""

galaxy_output = {}

for f in galaxies_fnames:
    with open(os.path.join(pathClusters, f)) as fr:
        cluster = json.load(fr)
    cluster_filename = f.split('.')[0]
    index_output += f'- [{cluster["name"]}](./{cluster_filename}/index.md)\n'
    galaxy_output[cluster_filename] = ""
    galaxy_output[cluster_filename] += f'# {cluster["name"]}\n'
    galaxy_output[cluster_filename] += f'{cluster["description"]}\n'
    for value in cluster["values"]:
        galaxy_output[cluster_filename] += f'## {value["value"]}\n'
        if 'description' in value:
           galaxy_output[cluster_filename] += f'{value["description"]}\n'

with open(os.path.join(pathSite, 'index.md'), "w") as index:
    index.write(index_output)

for f in galaxies_fnames:
    cluster_filename = f.split('.')[0]
    pathSiteCluster = os.path.join(pathSite, cluster_filename)
    if not os.path.exists(pathSiteCluster):
        os.mkdir(pathSiteCluster)
    with open(os.path.join(pathSiteCluster, 'index.md'), "w") as index:
        index.write(galaxy_output[cluster_filename])
