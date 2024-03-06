from modules.universe import Universe
from modules.site import IndexSite, StatisticsSite
from utils.helper import generate_relations_table

import multiprocessing
from multiprocessing import Pool

from concurrent.futures import ThreadPoolExecutor

import json
import os
import time
import sys

sys.setrecursionlimit(10000)

FILES_TO_IGNORE = []
CLUSTER_PATH = "../../clusters"
SITE_PATH = "./site/docs"
GALAXY_PATH = "../../galaxies"


def write_relations_table(cluster):
    if cluster.relationships:
        print(f"Writing {cluster.uuid}.md")
        with open(os.path.join(relation_path, f"{cluster.uuid}.md"), "w") as index:
            index.write(generate_relations_table(cluster))


def get_cluster_relationships(cluster_data):
    galaxy, cluster = cluster_data
    relationships = universe.get_relationships_with_levels(
        universe.galaxies[galaxy].clusters[cluster]
    )
    print(f"Processed {galaxy}, {cluster}")
    return cluster, galaxy, relationships


def get_deprecated_galaxy_files():
    deprecated_galaxy_files = []
    for f in os.listdir(GALAXY_PATH):
        with open(os.path.join(GALAXY_PATH, f)) as fr:
            galaxy_json = json.load(fr)
            if "namespace" in galaxy_json and galaxy_json["namespace"] == "deprecated":
                deprecated_galaxy_files.append(f)

    return deprecated_galaxy_files


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
            universe.add_galaxy(
                galaxy_name=galaxy_json["name"],
                json_file_name=galaxy,
                authors=galaxy_json["authors"],
                description=galaxy_json["description"],
            )
            for cluster in galaxy_json["values"]:
                universe.add_cluster(
                    galaxy_name=galaxy_json.get("name", None),
                    uuid=cluster.get("uuid", None),
                    description=cluster.get("description", None),
                    value=cluster.get("value", None),
                    meta=cluster.get("meta", None),
                )

    # Define the relationships between clusters
    for galaxy in galaxies_fnames:
        with open(os.path.join(CLUSTER_PATH, galaxy)) as fr:
            galaxy_json = json.load(fr)
            for cluster in galaxy_json["values"]:
                if "related" in cluster:
                    for related in cluster["related"]:
                        universe.define_relationship(
                            cluster["uuid"], related["dest-uuid"]
                        )

    tasks = []
    for galaxy_name, galaxy in universe.galaxies.items():
        for cluster_name, cluster in galaxy.clusters.items():
            tasks.append((galaxy_name, cluster_name))

    with Pool(processes=multiprocessing.cpu_count()) as pool:
        result = pool.map(get_cluster_relationships, tasks)

    for cluster, galaxy, relationships in result:
        universe.galaxies[galaxy].clusters[cluster].relationships = relationships

    print("All clusters processed.")

    print(f"Finished relations in {time.time() - start_time} seconds")

    # Write output
    if not os.path.exists(SITE_PATH):
        os.mkdir(SITE_PATH)

    index = IndexSite(SITE_PATH)
    index.add_content(
        "# MISP Galaxy\n\nThe MISP galaxy offers a streamlined approach for representing large entities, known as clusters, which can be linked to MISP events or attributes. Each cluster consists of one or more elements, represented as key-value pairs. MISP galaxy comes with a default knowledge base, encompassing areas like Threat Actors, Tools, Ransomware, and ATT&CK matrices. However, users have the flexibility to modify, update, replace, or share these elements according to their needs.\n\nClusters and vocabularies within MISP galaxy can be utilized in their original form or as a foundational knowledge base. The distribution settings for each cluster can be adjusted, allowing for either restricted or wide dissemination.\n\nAdditionally, MISP galaxies enable the representation of existing standards like the MITRE ATT&CK™ framework, as well as custom matrices.\n\nThe aim is to provide a core set of clusters for organizations embarking on analysis, which can be further tailored to include localized, private information or additional, shareable data.\n\nClusters serve as an open and freely accessible knowledge base, which can be utilized and expanded within [MISP](https://www.misp-project.org/) or other threat intelligence platforms.\n\n![Overview of the integration of MISP galaxy in the MISP Threat Intelligence Sharing Platform](https://raw.githubusercontent.com/MISP/misp-galaxy/aa41337fd78946a60aef3783f58f337d2342430a/doc/images/galaxy.png)\n\n## Publicly available clusters\n"
    )
    index.add_toc(universe.galaxies.values())
    index.add_content(
        "## Statistics\n\nYou can find some statistics about MISP galaxies [here](./statistics.md).\n\n"
    )
    index.add_content(
        "# Contributing\n\nIn the dynamic realm of threat intelligence, a variety of models and approaches exist to systematically organize, categorize, and delineate threat actors, hazards, or activity groups. We embrace innovative methodologies for articulating threat intelligence. The galaxy model is particularly versatile, enabling you to leverage and integrate methodologies that you trust and are already utilizing within your organization or community.\n\nWe encourage collaboration and contributions to the [MISP Galaxy JSON files](https://github.com/MISP/misp-galaxy/). Feel free to fork the project, enhance existing elements or clusters, or introduce new ones. Your insights are valuable - share them with us through a pull-request.\n"
    )
    index.write_entry()

    statistics = StatisticsSite(SITE_PATH)
    statistics.add_content("# MISP Galaxy Statistics\n\n")
    statistics.add_cluster_statistics(
        len(
            [
                cluster
                for galaxy in universe.galaxies.values()
                for cluster in galaxy.clusters.values()
            ]
        ),
        len(universe.private_clusters),
    )
    statistics.add_galaxy_statistics(universe.galaxies.values())
    statistics.add_relation_statistics(
        [
            cluster
            for galaxy in universe.galaxies.values()
            for cluster in galaxy.clusters.values()
        ]
    )
    statistics.add_synonym_statistics(
        [
            cluster
            for galaxy in universe.galaxies.values()
            for cluster in galaxy.clusters.values()
        ]
    )
    statistics.write_entry()

    for galaxy in universe.galaxies.values():
        galaxy.write_entry(SITE_PATH)

    for galaxy in universe.galaxies.values():
        galaxy_path = os.path.join(
            SITE_PATH, f"{galaxy.json_file_name}".replace(".json", "")
        )
        if not os.path.exists(galaxy_path):
            os.mkdir(galaxy_path)
        relation_path = os.path.join(galaxy_path, "relations")
        if not os.path.exists(relation_path):
            os.mkdir(relation_path)
        with open(os.path.join(relation_path, ".pages"), "w") as index:
            index.write(f"hide: true\n")

        with ThreadPoolExecutor(
            max_workers=(multiprocessing.cpu_count() * 4)
        ) as executor:
            executor.map(write_relations_table, galaxy.clusters.values())

    print(f"Finished in {time.time() - start_time} seconds")
