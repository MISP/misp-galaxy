#!/usr/bin/python

import json
import os

import validators

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
index_contributing = """

# Contributing

In the dynamic realm of threat intelligence, a variety of models and approaches exist to systematically organize, categorize, and delineate threat actors, hazards, or activity groups. We embrace innovative methodologies for articulating threat intelligence. The galaxy model is particularly versatile, enabling you to leverage and integrate methodologies that you trust and are already utilizing within your organization or community.

We encourage collaboration and contributions to the [MISP Galaxy JSON files](https://github.com/MISP/misp-galaxy/). Feel free to fork the project, enhance existing elements or clusters, or introduce new ones. Your insights are valuable - share them with us through a pull-request.

"""

galaxy_output = {}

for f in galaxies_fnames:
    with open(os.path.join(pathClusters, f)) as fr:
        cluster = json.load(fr)
    cluster_filename = f.split('.')[0]
    index_output += f'- [{cluster["name"]}](./{cluster_filename}/index.md)\n'
    galaxy_output[cluster_filename] = "---\n"
    galaxy_output[cluster_filename] += f'title: {cluster["name"]}\n'
    meta_description = cluster["description"].replace("\"", "-")
    galaxy_output[cluster_filename] += f'description: {meta_description}\n'
    galaxy_output[cluster_filename] += "---\n"
    galaxy_output[cluster_filename] += f'# {cluster["name"]}\n'
    galaxy_output[cluster_filename] += f'{cluster["description"]}\n'
    for value in cluster["values"]:
        galaxy_output[cluster_filename] += f'## {value["value"]}\n'
        galaxy_output[cluster_filename] += f'\n'
        if 'description' in value:
           galaxy_output[cluster_filename] += f'{value["description"]}\n'

        if 'meta' in value:
            if 'synonyms' in value['meta']:
                if value['meta']['synonyms']: # some cluster have an empty list of synomyms
                    galaxy_output[cluster_filename] += f'\n'
                    galaxy_output[cluster_filename] += f'??? info "Synonyms"\n'
                    galaxy_output[cluster_filename] += f'\n'
                    galaxy_output[cluster_filename] += f'     "synonyms" in the meta part typically refer to alternate names or labels that are associated with a particular {cluster["name"]}.\n\n'
                    galaxy_output[cluster_filename] += f'    | Known Synonyms      |\n'
                    galaxy_output[cluster_filename] += f'    |---------------------|\n'
                    for synonym in sorted(value['meta']['synonyms']):
                        galaxy_output[cluster_filename] += f'     | `{synonym}`      |\n'

        if 'uuid' in value:
           galaxy_output[cluster_filename] += f'\n'
           galaxy_output[cluster_filename] += f'??? tip "Internal MISP references"\n'
           galaxy_output[cluster_filename] += f'\n'
           galaxy_output[cluster_filename] += f'    UUID `{value["uuid"]}` which can be used as unique global reference for `{value["value"]}` in MISP communities and other software using the MISP galaxy\n'
           galaxy_output[cluster_filename] += f'\n'

        if 'meta' in value:
            if 'refs' in value['meta']:
               galaxy_output[cluster_filename] += f'\n'
               galaxy_output[cluster_filename] += f'??? info "External references"\n'
               galaxy_output[cluster_filename] += f'\n'

               for ref in value["meta"]["refs"]:
                   if validators.url(ref): # some ref are not actual URL (TODO: check galaxy cluster sources)
                      galaxy_output[cluster_filename] += f'     - [{ref}]({ref}) - :material-archive: :material-arrow-right: [webarchive](https://web.archive.org/web/*/{ref})\n'
                   else:
                      galaxy_output[cluster_filename] += f'     - {ref}\n'

               galaxy_output[cluster_filename] += f'\n'
            excluded_meta = ['synonyms', 'refs']
            galaxy_output[cluster_filename] += f'\n'
            galaxy_output[cluster_filename] += f'??? info "Associated metadata"\n'
            galaxy_output[cluster_filename] += f'\n'
            galaxy_output[cluster_filename] += f'    |Metadata key      |Value|\n'
            galaxy_output[cluster_filename] += f'    |---------------------|-----|\n'
            for meta in sorted(value['meta']):
                if meta in excluded_meta:
                    continue
                galaxy_output[cluster_filename] += f'     | `{meta}`      |{value["meta"][meta]}|\n'

index_output += index_contributing

with open(os.path.join(pathSite, 'index.md'), "w") as index:
    index.write(index_output)

for f in galaxies_fnames:
    cluster_filename = f.split('.')[0]
    pathSiteCluster = os.path.join(pathSite, cluster_filename)
    if not os.path.exists(pathSiteCluster):
        os.mkdir(pathSiteCluster)
    with open(os.path.join(pathSiteCluster, 'index.md'), "w") as index:
        index.write(galaxy_output[cluster_filename])
