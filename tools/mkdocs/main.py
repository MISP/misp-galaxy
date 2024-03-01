from modules.universe import Universe

import multiprocessing
from multiprocessing import Pool

import json
import os
import time
import sys

sys.setrecursionlimit(10000) 

FILES_TO_IGNORE = [] 
CLUSTER_PATH = "../../clusters"
SITE_PATH = "./site/docs"
GALAXY_PATH = "../../galaxies"

def save_cluster_relationships(cluster_data):
    # Unpack cluster data
    galaxy_name, cluster_name, cluster = cluster_data
    
    # Assuming `universe.get_relationships_with_levels` and `cluster.save_relationships`
    # are methods that can be called like this.
    relationships = universe.get_relationships_with_levels(cluster)
    cluster.save_relationships(relationships)
    print(f"Processed {galaxy_name}, {cluster_name}")

def get_deprecated_galaxy_files():
    deprecated_galaxy_files = []
    for f in os.listdir(GALAXY_PATH):
        with open(os.path.join(GALAXY_PATH, f)) as fr:
            galaxy_json = json.load(fr)
            if "namespace" in galaxy_json and galaxy_json["namespace"] == "deprecated":
                deprecated_galaxy_files.append(f)

    return deprecated_galaxy_files

def cluster_transform_to_link(cluster):
    placeholder = "__TMP__"
    section = (
        cluster
        .value.lower()
        .replace(" - ", placeholder)  # Replace " - " first
        .replace(" ", "-")
        .replace("/", "")
        .replace(":", "")
        .replace(placeholder, "-")
    )
    return f"[{cluster.value} ({cluster.uuid})](../../{cluster.galaxy.json_file_name}/index.md#{section})"

def galaxy_transform_to_link(galaxy):
    return f"[{galaxy.galaxy_name}](../../{galaxy.json_file_name}/index.md)"

def generate_relations_table(relationships):
    markdown = "|Cluster A | Galaxy A | Cluster B | Galaxy B | Level { .graph } |\n"
    markdown += "|--- | --- | --- | --- | --- | ---|\n"
    for from_cluster, to_cluster, level in relationships:
        from_galaxy = from_cluster.galaxy.galaxy_name
        to_galaxy = to_cluster.galaxy.galaxy_name
        markdown += f"{cluster_transform_to_link(from_cluster)} | {galaxy_transform_to_link(from_galaxy)} | {cluster_transform_to_link(to_cluster)} | {galaxy_transform_to_link(to_galaxy)} | {level}\n"
    return markdown

def generate_index_page(galaxies):
    index_output = "# MISP Galaxy\n\nThe MISP galaxy offers a streamlined approach for representing large entities, known as clusters, which can be linked to MISP events or attributes. Each cluster consists of one or more elements, represented as key-value pairs. MISP galaxy comes with a default knowledge base, encompassing areas like Threat Actors, Tools, Ransomware, and ATT&CK matrices. However, users have the flexibility to modify, update, replace, or share these elements according to their needs.\n\nClusters and vocabularies within MISP galaxy can be utilized in their original form or as a foundational knowledge base. The distribution settings for each cluster can be adjusted, allowing for either restricted or wide dissemination.\n\nAdditionally, MISP galaxies enable the representation of existing standards like the MITRE ATT&CK™ framework, as well as custom matrices.\n\nThe aim is to provide a core set of clusters for organizations embarking on analysis, which can be further tailored to include localized, private information or additional, shareable data.\n\nClusters serve as an open and freely accessible knowledge base, which can be utilized and expanded within [MISP](https://www.misp-project.org/) or other threat intelligence platforms.\n\n![Overview of the integration of MISP galaxy in the MISP Threat Intelligence Sharing Platform](https://raw.githubusercontent.com/MISP/misp-galaxy/aa41337fd78946a60aef3783f58f337d2342430a/doc/images/galaxy.png)\n\n## Publicly available clusters\n"
    for galaxy in galaxies:
        index_output += f"- [{galaxy.galaxy_name}](./{galaxy.json_file_name}/index.md)\n"
    index_output += "## Statistics\n\nYou can find some statistics about MISP galaxies [here](./statistics.md).\n"
    index_output += "# Contributing\n\nIn the dynamic realm of threat intelligence, a variety of models and approaches exist to systematically organize, categorize, and delineate threat actors, hazards, or activity groups. We embrace innovative methodologies for articulating threat intelligence. The galaxy model is particularly versatile, enabling you to leverage and integrate methodologies that you trust and are already utilizing within your organization or community.\n\nWe encourage collaboration and contributions to the [MISP Galaxy JSON files](https://github.com/MISP/misp-galaxy/). Feel free to fork the project, enhance existing elements or clusters, or introduce new ones. Your insights are valuable - share them with us through a pull-request.\n"
    return index_output

if __name__ == "__main__":
    start_time = time.time()
    universe = Universe()

    FILES_TO_IGNORE.extend(get_deprecated_galaxy_files())
    galaxies_fnames = []
    for f in os.listdir(CLUSTER_PATH):
        if ".json" in f and f not in FILES_TO_IGNORE:
            galaxies_fnames.append(f)
    galaxies_fnames.sort()

    # Create the universe of clusters and galaxies
    for galaxy in galaxies_fnames:
        with open(os.path.join(CLUSTER_PATH, galaxy)) as fr:
            galaxy_json = json.load(fr)
            universe.add_galaxy(galaxy_name=galaxy_json["name"], json_file_name=galaxy, authors=galaxy_json["authors"], description=galaxy_json["description"])
            for cluster in galaxy_json["values"]:
                universe.add_cluster(
                galaxy_name=galaxy_json.get("name", None),
                uuid=cluster.get("uuid", None),
                description=cluster.get("description", None),
                value=cluster.get("value", None),
                meta=cluster.get("meta", None)
            )


    # Define the relationships between clusters
    for galaxy in galaxies_fnames:
        with open(os.path.join(CLUSTER_PATH, galaxy)) as fr:
            galaxy_json = json.load(fr)
            for cluster in galaxy_json["values"]:
                if "related" in cluster:
                    for related in cluster["related"]:
                        universe.define_relationship(cluster["uuid"], related["dest-uuid"])
    

    # # Save relationships to clusters
    # for galaxy in universe.galaxies.values():
    #     for cluster in galaxy.clusters.values():
    #         cluster.save_relationships(universe.get_relationships_with_levels(cluster))

    tasks = []
    for galaxy_name, galaxy in universe.galaxies.items():
        for cluster_name, cluster in galaxy.clusters.items():
            tasks.append((galaxy_name, cluster_name, cluster))

    with Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.map(save_cluster_relationships, tasks)
    print("All clusters processed.")

    print(f"Finished relations in {time.time() - start_time} seconds")

    # Write output
    if not os.path.exists(SITE_PATH):
        os.mkdir(SITE_PATH)

    with open(os.path.join(SITE_PATH, "index.md"), "w") as index:
        index.write(generate_index_page(universe.galaxies.values()))

    for galaxy in universe.galaxies.values():
        galaxy.write_entry(SITE_PATH)

    for galaxy in universe.galaxies.values():
        if not os.path.exists(GALAXY_PATH):
            os.mkdir(GALAXY_PATH)
        relation_path = os.path.join(GALAXY_PATH, "relations")
        if not os.path.exists(relation_path):
            os.mkdir(relation_path)
        with open(os.path.join(relation_path, ".pages"), "w") as index:
            index.write(f"hide: true\n")

        for cluster in galaxy.clusters.values():
            if cluster.relationships:
                with open(os.path.join(relation_path, f"{cluster.uuid}.md"), "w") as index:
                    index.write(generate_relations_table(cluster.relationships))

    print(f"Finished in {time.time() - start_time} seconds")

    # relationships = universe.get_relationships_with_levels("Banker", "f0ec2df5-2e38-4df3-970d-525352006f2e")
    # print(relationships)


    # markdown_table = generate_markdown_table(relationships)
    # print(markdown_table)