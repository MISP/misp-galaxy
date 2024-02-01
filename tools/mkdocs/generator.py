#!/usr/bin/python

import json
import operator
import os
import re
from typing import List

import validators

CLUSTER_PATH = '../../clusters'
SITE_PATH = './site/docs'
# PROJECTS_PATH = './site/projects'

FILES_TO_IGNORE = [] # if you want to skip a specific cluster in the generation

# Variables for statistics
public_relations_count = 0
private_relations_count = 0
private_clusters = []
public_clusters_dict = {}
relation_count_dict = {}
synonyms_count_dict = {}
empty_uuids_dict = {}

INTRO = """
# MISP Galaxy

The MISP galaxy offers a streamlined approach for representing large entities, known as clusters, which can be linked to MISP events or attributes. Each cluster consists of one or more elements, represented as key-value pairs. MISP galaxy comes with a default knowledge base, encompassing areas like Threat Actors, Tools, Ransomware, and ATT&CK matrices. However, users have the flexibility to modify, update, replace, or share these elements according to their needs.

Clusters and vocabularies within MISP galaxy can be utilized in their original form or as a foundational knowledge base. The distribution settings for each cluster can be adjusted, allowing for either restricted or wide dissemination.

Additionally, MISP galaxies enable the representation of existing standards like the MITRE ATT&CK™ framework, as well as custom matrices.

The aim is to provide a core set of clusters for organizations embarking on analysis, which can be further tailored to include localized, private information or additional, shareable data.

Clusters serve as an open and freely accessible knowledge base, which can be utilized and expanded within [MISP](https://www.misp-project.org/) or other threat intelligence platforms.

![Overview of the integration of MISP galaxy in the MISP Threat Intelligence Sharing Platform](https://raw.githubusercontent.com/MISP/misp-galaxy/aa41337fd78946a60aef3783f58f337d2342430a/doc/images/galaxy.png)

## Publicly available clusters

"""

STATISTICS= """
## Statistics

You can find some statistics about MISP galaxies [here](./statistics.md).

"""

CONTRIBUTING = """

# Contributing

In the dynamic realm of threat intelligence, a variety of models and approaches exist to systematically organize, categorize, and delineate threat actors, hazards, or activity groups. We embrace innovative methodologies for articulating threat intelligence. The galaxy model is particularly versatile, enabling you to leverage and integrate methodologies that you trust and are already utilizing within your organization or community.

We encourage collaboration and contributions to the [MISP Galaxy JSON files](https://github.com/MISP/misp-galaxy/). Feel free to fork the project, enhance existing elements or clusters, or introduce new ones. Your insights are valuable - share them with us through a pull-request.

"""

class Galaxy():
    def __init__(self, cluster_list: List[dict], authors, description, name, json_file_name):
        self.cluster_list = cluster_list
        self.authors = authors
        self.description = description
        self.name = name
        self.json_file_name = json_file_name
        self.clusters = self._create_clusters()
        self.entry = ""

    def _create_metadata_entry(self):
        self.entry += "---\n"
        self.entry += f'title: {self.name}\n'
        meta_description = self.description.replace("\"", "-")
        self.entry += f'description: {meta_description}\n'
        self.entry += "---\n"

    def _create_title_entry(self):
        self.entry += f'# {self.name}\n'

    def _create_description_entry(self):
        self.entry += f'{self.description}\n'

    def _create_authors_entry(self):
        if self.authors:
            self.entry += f'\n'
            self.entry += f'??? info "Authors"\n'
            self.entry += f'\n'
            self.entry += f'     | Authors and/or Contributors|\n'
            self.entry += f'     |----------------------------|\n'
            for author in self.authors:
                self.entry += f'     |{author}|\n'

    def _create_clusters(self):
        # global public_clusters_dict
        clusters = []
        for cluster in self.cluster_list:
            clusters.append(Cluster(
                value=cluster.get('value', None),
                description=cluster.get('description', None),
                uuid=cluster.get('uuid', None),
                date=cluster.get('date', None),
                related_list=cluster.get('related', None),
                meta=cluster.get('meta', None),
                galaxie=self.json_file_name
            ))
        return clusters
    
    def _create_clusters_entry(self, cluster_dict):
        for cluster in self.clusters:
            self.entry += cluster.create_entry(cluster_dict)

    def create_entry(self, cluster_dict):
        self._create_metadata_entry()
        self._create_title_entry()
        self._create_description_entry()
        self._create_authors_entry()
        self._create_clusters_entry(cluster_dict)
        return self.entry
    
    def write_entry(self, path, cluster_dict):
        self.create_entry(cluster_dict)
        galaxy_path = os.path.join(path, self.json_file_name)
        if not os.path.exists(galaxy_path):
            os.mkdir(galaxy_path)
        with open(os.path.join(galaxy_path, 'index.md'), "w") as index:
            index.write(self.entry)

class Cluster():
    def __init__(self, description, uuid, date, value, related_list, meta, galaxie):
        self.description = description
        self.uuid = uuid
        self.date = date
        self.value = value
        self.related_list = related_list
        self.meta = meta
        self.entry = ""
        self.galaxie = galaxie
        
        global public_clusters_dict
        if self.galaxie:
            public_clusters_dict[self.uuid] = self.galaxie

    def _create_title_entry(self):
        self.entry += f'## {self.value}\n'
        self.entry += f'\n'

    def _create_description_entry(self):
        if self.description:
            self.entry += f'{self.description}\n'

    def _create_synonyms_entry(self):
        if isinstance(self.meta, dict) and self.meta.get('synonyms'):
            self.entry += f'\n'
            self.entry += f'??? info "Synonyms"\n'
            self.entry += f'\n'
            self.entry += f'     "synonyms" in the meta part typically refer to alternate names or labels that are associated with a particular {self.value}.\n\n'
            self.entry += f'    | Known Synonyms      |\n'
            self.entry += f'    |---------------------|\n'
            global synonyms_count_dict
            synonyms_count = 0
            for synonym in sorted(self.meta['synonyms']):
                synonyms_count += 1
                self.entry += f'     | `{synonym}`      |\n'
            synonyms_count_dict[self.value] = synonyms_count

    def _create_uuid_entry(self):
        if self.uuid:
            self.entry += f'\n'
            self.entry += f'??? tip "Internal MISP references"\n'
            self.entry += f'\n'
            self.entry += f'    UUID `{self.uuid}` which can be used as unique global reference for `{self.value}` in MISP communities and other software using the MISP galaxy\n'
            self.entry += f'\n'

    def _create_refs_entry(self):
        if isinstance(self.meta, dict) and self.meta.get('refs'):
            self.entry += f'\n'
            self.entry += f'??? info "External references"\n'
            self.entry += f'\n'

            for ref in self.meta['refs']:
                if validators.url(ref):
                    self.entry += f'     - [{ref}]({ref}) - :material-archive: :material-arrow-right: [webarchive](https://web.archive.org/web/*/{ref})\n'
                else:
                    self.entry += f'     - {ref}\n'
            
            self.entry += f'\n'

    def _create_associated_metadata_entry(self):
        if isinstance(self.meta, dict):
            excluded_meta = ['synonyms', 'refs']
            self.entry += f'\n'
            self.entry += f'??? info "Associated metadata"\n'
            self.entry += f'\n'
            self.entry += f'    |Metadata key      |Value|\n'
            self.entry += f'    |------------------|-----|\n'
            for meta in sorted(self.meta.keys()):
                if meta not in excluded_meta:
                    self.entry += f'    | {meta} | {self.meta[meta]} |\n'
    

    def get_related_clusters(self, cluster_dict, depth=-1, visited=None, level=1):
        global public_relations_count
        global private_relations_count
        global private_clusters
        global empty_uuids_dict
        empty_uuids = 0

        if visited is None:
            visited = set()

        related_clusters = []
        if depth == 0 or not self.related_list or self.uuid in visited:
            return related_clusters

        visited.add(self.uuid)

        for cluster in self.related_list:
            dest_uuid = cluster["dest-uuid"]

            # Cluster is private
            if dest_uuid not in cluster_dict:
                # Check if UUID is empty
                if not dest_uuid:
                    empty_uuids += 1
                    continue
                private_relations_count += 1
                if dest_uuid not in private_clusters:
                    private_clusters.append(dest_uuid)
                related_clusters.append((self, Cluster(value="Private Cluster", uuid=dest_uuid, date=None, description=None, related_list=None, meta=None, galaxie=None), level))
                continue

            related_cluster = cluster_dict[dest_uuid]

            public_relations_count += 1

            related_clusters.append((self, related_cluster, level))
            
            if (depth > 1 or depth == -1) and related_cluster.uuid not in visited:
                new_depth = depth - 1 if depth > 1 else -1
                related_clusters += related_cluster.get_related_clusters(depth=new_depth, visited=visited, cluster_dict=cluster_dict, level=level+1)

        if empty_uuids > 0:
            empty_uuids_dict[self.value] = empty_uuids

        for cluster in related_clusters:
            if (cluster[1], cluster[0], level) in related_clusters:
                related_clusters.remove(cluster)
        
        return related_clusters

    def _create_related_entry(self):
        self.entry += f'\n'
        self.entry += f'??? info "Related clusters"\n'
        self.entry += f'\n'
        # self.entry += f'To see the related clusters, click [here](./{self.galaxie}/{self.uuid}.md).\n'
        self.entry += f'    To see the related clusters, click [here](./relations/{self.uuid}.md).\n'

    def _get_related_entry(self, relations):
        output = ""
        output += f'## Related clusters for {self.value}\n'
        output += f'\n'
        output += f'| Cluster A | Cluster B | Level |\n'
        output += f'|-----------|-----------|-------|\n'
        for relation in relations:
            output += f'| {relation[0].value}  ({relation[0].uuid}) | {relation[1].value}  ({relation[1].uuid}) | {relation[2]} |\n'
        return output
     
    def create_entry(self, cluster_dict):
        self._create_title_entry()
        self._create_description_entry()
        self._create_synonyms_entry()
        self._create_uuid_entry()
        self._create_refs_entry()
        self._create_associated_metadata_entry()
        if self.related_list:
            self._create_related_entry()
            self._write_relations(cluster_dict, SITE_PATH)
        return self.entry
    
    def _write_relations(self, cluster_dict, path):
        related_clusters = self.get_related_clusters(cluster_dict)
        global relation_count_dict
        relation_count_dict[self.value] = len(related_clusters)
        galaxy_path = os.path.join(path, self.galaxie)
        if not os.path.exists(galaxy_path):
            os.mkdir(galaxy_path)
        relation_path = os.path.join(galaxy_path, 'relations')
        if not os.path.exists(relation_path):
            os.mkdir(relation_path)
        with open(os.path.join(relation_path, ".pages"), "w") as index:
            index.write(f'hide: true\n')
        with open(os.path.join(relation_path, f'{self.uuid}.md'), "w") as index:
            index.write(self._get_related_entry(related_clusters))
        
def create_index(galaxies):
    index_output = INTRO
    index_output += STATISTICS
    for galaxie in galaxies:
        index_output += f'- [{galaxie.name}](./{galaxie.json_file_name}/index.md)\n'
    index_output += CONTRIBUTING
    return index_output

def create_galaxies(galaxies, cluster_dict):
    galaxy_output = {}
    for galaxie in galaxies:
        galaxy_output[galaxie.json_file_name] = galaxie.create_entry(cluster_dict)
    return galaxy_output

def create_xy_chart(title, width, height, x_axis, y_axis, bar):
    output = ""
    output += f'```mermaid\n'
    output += f'---\n'
    output += f'config:\n'
    output += f'  xyChart:\n'
    output += f'    width: {width}\n'
    output += f'    height: {height}\n'
    output += f'---\n'
    output += f'xychart-beta\n'
    output += f'  title "{title}"\n'
    output += f'  x-axis [{x_axis}]\n'
    output += f'  y-axis "{y_axis}"\n'
    output += f'  bar {bar}\n'
    output += f'```\n'
    output += f'\n'
    return output

def create_pie_chart(title, cakepieces):
    output = ""
    output += f'```mermaid\n'
    output += f'pie showData\n'
    output += f'  title {title}\n'
    for cakepiece in cakepieces:
        output += f'  "{cakepiece[0]}" : {cakepiece[1]}\n'
    output += f'```\n'
    output += f'\n'
    return output
    
def get_top_x(dict, x, big_to_small=True):
    sorted_dict = sorted(dict.items(), key=operator.itemgetter(1), reverse=big_to_small)[:x]
    top_x = [re.sub(r"[^A-Za-z0-9 ]", "", key) for key, value in sorted_dict]
    top_x = ", ".join(top_x)
    top_x_values = sorted(dict.values(), reverse=big_to_small)[:x]
    return top_x, top_x_values

def create_statistics():
    statistic_output = ""

    statistic_output += f'# Cluster statistics\n'
    statistic_output += f'## Number of clusters\n'
    statistic_output += create_pie_chart("Number of clusters", [("Public clusters", len(public_clusters_dict)), ("Private clusters", len(private_clusters))])

    statistic_output += f'## Galaxies with the most clusters\n'
    galaxy_counts = {}
    for galaxy in public_clusters_dict.values():
        galaxy_counts[galaxy] = galaxy_counts.get(galaxy, 0) + 1
    top_galaxies, top_galaxies_values = get_top_x(galaxy_counts, 25)
    statistic_output += create_xy_chart("Galaxies with the most clusters", 2500, 500, top_galaxies, "Number of clusters", top_galaxies_values)

    statistic_output += f'## Galaxies with the least clusters\n'
    flop_galaxies, flop_galaxies_values = get_top_x(galaxy_counts, 25, False)
    statistic_output += create_xy_chart("Galaxies with the least clusters", 2500, 500, flop_galaxies, "Number of clusters", flop_galaxies_values)
    
    galaxy_number = 0
    for galaxy in public_clusters_dict.values():
        galaxy_number += 1
    statistic_output += f'**Average number of clusters per galaxy**: {len(public_clusters_dict) / galaxy_number}\n'

    statistic_output += f'# Relation statistics\n'
    statistic_output += f'## Number of relations\n'
    statistic_output += create_pie_chart("Number of relations", [("Public relations", public_relations_count), ("Private relations", private_relations_count)])

    statistic_output += f'**Average number of relations per cluster**: {sum(relation_count_dict.values()) / len(relation_count_dict)}\n'

    statistic_output += f'## Cluster with the most relations\n'
    top_25_relation, top_25_relation_values = get_top_x(relation_count_dict, 25)
    statistic_output += create_xy_chart("Cluster with the most relations", 2500, 500, top_25_relation, "Number of relations", top_25_relation_values)

    statistic_output += f'## Cluster with the least relations\n'
    top_25_relation, top_25_relation_values = get_top_x(relation_count_dict, 25, False)
    statistic_output += create_xy_chart("Cluster with the least relations", 2500, 500, top_25_relation, "Number of relations", top_25_relation_values)

    statistic_output += f'# Synonyms statistics\n'
    statistic_output += f'## Cluster with the most synonyms\n'
    top_25_synonyms, top_25_synonyms_values = get_top_x(synonyms_count_dict, 25)
    statistic_output += create_xy_chart("Cluster with the most synonyms", 2500, 500, top_25_synonyms, "Number of synonyms", top_25_synonyms_values)

    statistic_output += f'## Cluster with the least synonyms\n'
    top_25_synonyms, top_25_synonyms_values = get_top_x(synonyms_count_dict, 25, False)
    statistic_output += create_xy_chart("Cluster with the least synonyms", 2500, 500, top_25_synonyms, "Number of synonyms", top_25_synonyms_values)

    statistic_output += f'# Empty UUIDs statistics\n'
    statistic_output += f'**Number of empty UUIDs**: {sum(empty_uuids_dict.values())}\n'
    statistic_output += f'\n'
    statistic_output += f'**Empty UUIDs per cluster**: {empty_uuids_dict}\n'


    print(f"Public relations: {public_relations_count}")
    print(f"Private relations: {private_relations_count}")
    print(f"Total relations: {public_relations_count + private_relations_count}")
    print(f"Percetage of private relations: {private_relations_count / (public_relations_count + private_relations_count) * 100}%")
    print(f"Private clusters: {len(private_clusters)}")
    print(f"Public clusters: {len(public_clusters_dict)}")
    print(f"Total clusters: {len(private_clusters) + len(public_clusters_dict)}")
    print(f"Percentage of private clusters: {len(private_clusters) / (len(private_clusters) + len(public_clusters_dict)) * 100}%")
    print(f"Average number of relations per cluster: {sum(relation_count_dict.values()) / len(relation_count_dict)}")
    print(f"Max number of relations per cluster: {max(relation_count_dict.values())} from {max(relation_count_dict, key=relation_count_dict.get)}")
    print(f"Min number of relations per cluster: {min(relation_count_dict.values())} from {min(relation_count_dict, key=relation_count_dict.get)}")
    print(f"Average number of synonyms per cluster: {sum(synonyms_count_dict.values()) / len(synonyms_count_dict)}")
    print(f"Max number of synonyms per cluster: {max(synonyms_count_dict.values())} from {max(synonyms_count_dict, key=synonyms_count_dict.get)}")
    print(f"Min number of synonyms per cluster: {min(synonyms_count_dict.values())} from {min(synonyms_count_dict, key=synonyms_count_dict.get)}") 
    print(f"Number of empty UUIDs: {sum(empty_uuids_dict.values())}")
    print(f"Empty UUIDs per cluster: {empty_uuids_dict}")
    print(sorted(relation_count_dict.items(), key=operator.itemgetter(1), reverse=True)[:30])

    return statistic_output

def main():
    galaxies_fnames = []
    for f in os.listdir(CLUSTER_PATH):
        if '.json' in f and f not in FILES_TO_IGNORE:
            galaxies_fnames.append(f)
    galaxies_fnames.sort()

    galaxies = []
    for galaxy in galaxies_fnames:
        with open(os.path.join(CLUSTER_PATH, galaxy)) as fr:
            galaxie_json = json.load(fr)
            galaxies.append(Galaxy(galaxie_json['values'], galaxie_json['authors'], galaxie_json['description'], galaxie_json['name'], galaxy.split('.')[0]))

    cluster_dict = {}
    for galaxy in galaxies:
        for cluster in galaxy.clusters:
            cluster_dict[cluster.uuid] = cluster

    # Write files
    if not os.path.exists(SITE_PATH):
        os.mkdir(SITE_PATH)

    # for galaxy in galaxies:
    #     galaxy.write_entry(SITE_PATH, cluster_dict)
        
    count = 3
    for galaxy in galaxies:
        galaxy.write_entry(SITE_PATH, cluster_dict)
        count -= 1
        if count == 0:
            break

    index_output = create_index(galaxies)
    statistic_output = create_statistics()

    with open(os.path.join(SITE_PATH, 'index.md'), "w") as index:
        index.write(index_output)

    with open(os.path.join(SITE_PATH, 'statistics.md'), "w") as index:
        index.write(statistic_output)

if __name__ == "__main__":
    main()

    # test = cluster_dict['f0ec2df5-2e38-4df3-970d-525352006f2e']
    # test = cluster_dict['d7247cf9-13b6-4781-b789-a5f33521633b']
    # clusters = test.get_related_clusters()
    # print(clusters)
    # print(len(clusters))
    # print("```mermaid")
    # print(f"graph TD")
    # for cluster in clusters:
    #     print(f"{cluster[0].uuid}[{cluster[0].value}] --- {cluster[1].uuid}[{cluster[1].value}]")
    # print("```")
