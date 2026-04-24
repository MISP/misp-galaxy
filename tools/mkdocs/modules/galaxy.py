from modules.cluster import Cluster
from utils.helper import name_to_section
from typing import List
import os


class Galaxy:
    def __init__(
        self,
        galaxy_name: str,
        json_file_name: str,
        authors: List[str],
        description: str,
        kill_chain_order=None,
    ):
        self.galaxy_name = galaxy_name
        self.json_file_name = json_file_name
        self.authors = authors
        self.description = description
        self.kill_chain_order = kill_chain_order or {}

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
        entry += self._create_matrix_entry()
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

    def _create_matrix_entry(self):
        if not self.kill_chain_order:
            return ""

        entry = "\n## Matrix view\n"
        entry += "This view groups clusters by matrix phase for quicker navigation.\n\n"

        mapped_clusters = {matrix: {phase: [] for phase in phases} for matrix, phases in self.kill_chain_order.items()}
        seen_entries = {matrix: {phase: set() for phase in phases} for matrix, phases in self.kill_chain_order.items()}

        for cluster in self.clusters.values():
            if not isinstance(cluster.meta, dict):
                continue
            kill_chain_values = cluster.meta.get("kill_chain")
            if not isinstance(kill_chain_values, list):
                continue

            for kill_chain in kill_chain_values:
                parts = str(kill_chain).split(":")
                if len(parts) < 2:
                    continue

                if len(parts) >= 3:
                    matrix = parts[-2]
                    phase = parts[-1]
                else:
                    matrix = parts[0]
                    phase = parts[1]

                if matrix not in mapped_clusters or phase not in mapped_clusters[matrix]:
                    continue

                if cluster.uuid in seen_entries[matrix][phase]:
                    continue

                mapped_clusters[matrix][phase].append(cluster)
                seen_entries[matrix][phase].add(cluster.uuid)

        for matrix, phases in self.kill_chain_order.items():
            if len(self.kill_chain_order) > 1:
                entry += f"### {matrix}\n\n"

            entry += f"| {' | '.join(phases)} |\n"
            entry += f"| {' | '.join(['---'] * len(phases))} |\n"

            row_cells = []
            for phase in phases:
                clusters = sorted(
                    mapped_clusters[matrix][phase], key=lambda cluster: cluster.value.lower()
                )
                if not clusters:
                    row_cells.append(" ")
                    continue
                links = [
                    f"[{cluster.value}](#{name_to_section(cluster.value)})"
                    for cluster in clusters
                ]
                row_cells.append("<br>".join(links))

            entry += f"| {' | '.join(row_cells)} |\n\n"

        return entry

    def _create_clusters_entry(self):
        entry = ""
        for cluster in self.clusters.values():
            entry += cluster.generate_entry()
        return entry
