from modules.cluster import Cluster
from typing import List
import os


class Galaxy:
    def __init__(
        self,
        galaxy_name: str,
        json_file_name: str,
        authors: List[str],
        description: str,
    ):
        self.galaxy_name = galaxy_name
        self.json_file_name = json_file_name
        self.authors = authors
        self.description = description

        self.clusters = {}  # Maps uuid to Cluster objects

    def add_cluster(self, uuid, description, value, meta):
        if uuid not in self.clusters:
            self.clusters[uuid] = Cluster(
                uuid=uuid, galaxy=self, description=description, value=value, meta=meta
            )

    def write_entry(self, path):
        galaxy_path = os.path.join(path, f"{self.json_file_name}".replace(".json", ""))
        if not os.path.exists(galaxy_path):
            os.mkdir(galaxy_path)
        with open(os.path.join(galaxy_path, "index.md"), "w") as index:
            index.write(self.generate_entry())

    def generate_entry(self):
        entry = ""
        entry += self._create_metadata_entry()
        entry += self._create_title_entry()
        entry += self._create_description_entry()
        entry += self._create_authors_entry()
        entry += self._create_clusters_entry()
        return entry

    def _create_metadata_entry(self):
        entry = ""
        entry += "---\n"
        entry += f"title: {self.galaxy_name}\n"
        meta_description = self.description.replace('"', "-")
        entry += f"description: {meta_description}\n"
        entry += "---\n"
        return entry

    def _create_title_entry(self):
        entry = ""
        entry += f"[Hide Navigation](#){{ .md-button #toggle-navigation }}\n"
        entry += f"[Hide TOC](#){{ .md-button #toggle-toc }}\n"
        entry += f"<div class=\"clearfix\"></div>\n"
        entry += f"[Edit :material-pencil:](https://github.com/MISP/misp-galaxy/edit/main/clusters/{self.json_file_name}){{ .md-button }}\n"
        entry += f"# {self.galaxy_name}\n"
        return entry

    def _create_description_entry(self):
        entry = ""
        entry += f"{self.description}\n"
        return entry

    def _create_authors_entry(self):
        entry = ""
        if self.authors:
            entry += f"\n"
            entry += f'??? info "Authors"\n'
            entry += f"\n"
            entry += f"     | Authors and/or Contributors|\n"
            entry += f"     |----------------------------|\n"
            for author in self.authors:
                entry += f"     |{author}|\n"
        return entry

    def _create_clusters_entry(self):
        entry = ""
        for cluster in self.clusters.values():
            entry += cluster.generate_entry()
        return entry
