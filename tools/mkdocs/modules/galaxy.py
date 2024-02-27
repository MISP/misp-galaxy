from modules.cluster import Cluster
from typing import List
import os

class Galaxy:
    def __init__(
        self, cluster_list: List[dict], authors, description, name, json_file_name
    ):
        self.cluster_list = cluster_list
        self.authors = authors
        self.description = description
        self.name = name
        self.json_file_name = json_file_name
        self.clusters = self._create_clusters()
        self.entry = ""

    def _create_metadata_entry(self):
        self.entry += "---\n"
        self.entry += f"title: {self.name}\n"
        meta_description = self.description.replace('"', "-")
        self.entry += f"description: {meta_description}\n"
        self.entry += "---\n"

    def _create_title_entry(self):
        self.entry += f"# {self.name}\n"

    def _create_description_entry(self):
        self.entry += f"{self.description}\n"

    def _create_authors_entry(self):
        if self.authors:
            self.entry += f"\n"
            self.entry += f'??? info "Authors"\n'
            self.entry += f"\n"
            self.entry += f"     | Authors and/or Contributors|\n"
            self.entry += f"     |----------------------------|\n"
            for author in self.authors:
                self.entry += f"     |{author}|\n"

    def _create_clusters(self):
        clusters = []
        for cluster in self.cluster_list:
            clusters.append(
                Cluster(
                    value=cluster.get("value", None),
                    description=cluster.get("description", None),
                    uuid=cluster.get("uuid", None),
                    date=cluster.get("date", None),
                    related_list=cluster.get("related", None),
                    meta=cluster.get("meta", None),
                    galaxy=self,
                )
            )
        return clusters

    def _create_clusters_entry(self, cluster_dict, path):
        for cluster in self.clusters:
            self.entry += cluster.create_entry(cluster_dict, path)

    def create_entry(self, cluster_dict, path):
        self._create_metadata_entry()
        self._create_title_entry()
        self._create_description_entry()
        self._create_authors_entry()
        self._create_clusters_entry(cluster_dict, path)
        return self.entry

    def write_entry(self, path, cluster_dict):
        self.create_entry(cluster_dict, path)
        galaxy_path = os.path.join(path, self.json_file_name)
        if not os.path.exists(galaxy_path):
            os.mkdir(galaxy_path)
        with open(os.path.join(galaxy_path, "index.md"), "w") as index:
            index.write(self.entry)