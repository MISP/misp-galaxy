import os
import validators


class Cluster:
    def __init__(
        self, description, uuid, date, value, related_list, meta, galaxy
    ):
        self.description = description
        self.uuid = uuid
        self.date = date
        self.value = value
        self.related_list = related_list
        self.meta = meta
        self.galaxy = galaxy

        self.entry = ""
        self.statistics = None

    def __lt__(self, other):
        return self.uuid < other.uuid

    def set_statistics(self, statistics):
        self.statistics = statistics

    def _create_title_entry(self):
        self.entry += f"## {self.value}\n"
        self.entry += f"\n"

    def _create_description_entry(self):
        if self.description:
            self.entry += f"{self.description}\n"

    def _create_synonyms_entry(self):
        if isinstance(self.meta, dict) and self.meta.get("synonyms"):
            self.entry += f"\n"
            self.entry += f'??? info "Synonyms"\n'
            self.entry += f"\n"
            self.entry += f'     "synonyms" in the meta part typically refer to alternate names or labels that are associated with a particular {self.value}.\n\n'
            self.entry += f"    | Known Synonyms      |\n"
            self.entry += f"    |---------------------|\n"
            synonyms_count = 0
            for synonym in sorted(self.meta["synonyms"]):
                synonyms_count += 1
                self.entry += f"     | `{synonym}`      |\n"
            self.statistics.synonyms_count_dict[self.uuid] = synonyms_count

    def _create_uuid_entry(self):
        if self.uuid:
            self.entry += f"\n"
            self.entry += f'??? tip "Internal MISP references"\n'
            self.entry += f"\n"
            self.entry += f"    UUID `{self.uuid}` which can be used as unique global reference for `{self.value}` in MISP communities and other software using the MISP galaxy\n"
            self.entry += f"\n"

    def _create_refs_entry(self):
        if isinstance(self.meta, dict) and self.meta.get("refs"):
            self.entry += f"\n"
            self.entry += f'??? info "External references"\n'
            self.entry += f"\n"

            for ref in self.meta["refs"]:
                if validators.url(ref):
                    self.entry += f"     - [{ref}]({ref}) - :material-archive: :material-arrow-right: [webarchive](https://web.archive.org/web/*/{ref})\n"
                else:
                    self.entry += f"     - {ref}\n"

            self.entry += f"\n"

    def _create_associated_metadata_entry(self):
        if isinstance(self.meta, dict):
            excluded_meta = ["synonyms", "refs"]
            self.entry += f"\n"
            self.entry += f'??? info "Associated metadata"\n'
            self.entry += f"\n"
            self.entry += f"    |Metadata key {{ .no-filter }}      |Value|\n"
            self.entry += f"    |-----------------------------------|-----|\n"
            for meta in sorted(self.meta.keys()):
                if meta not in excluded_meta:
                    self.entry += f"    | {meta} | {self.meta[meta]} |\n"

    def get_related_clusters(
        self, cluster_dict, depth=-1, visited=None, level=1, related_private_clusters={}
    ):
        empty_uuids = 0

        if visited is None:
            visited = {}

        related_clusters = []
        if depth == 0 or not self.related_list:
            return related_clusters

        if self.uuid in visited and visited[self.uuid] <= level:
            return related_clusters
        else:
            visited[self.uuid] = level

        for cluster in self.related_list:
            dest_uuid = cluster["dest-uuid"]

            # Cluster is private
            if dest_uuid not in cluster_dict:
                # Check if UUID is empty
                if not dest_uuid:
                    empty_uuids += 1
                    continue
                self.statistics.private_relations_count += 1
                if dest_uuid not in self.statistics.private_clusters:
                    self.statistics.private_clusters.append(dest_uuid)
                if dest_uuid in related_private_clusters:
                    related_clusters.append(
                        (
                            self,
                            related_private_clusters[dest_uuid],
                            level,
                        )
                    )
                else:
                    related_clusters.append(
                        (
                            self,
                            Cluster(
                                value="Private Cluster",
                                uuid=dest_uuid,
                                date=None,
                                description=None,
                                related_list=None,
                                meta=None,
                                galaxy=None,
                            ),
                            level,
                        )
                    )
                    related_private_clusters[dest_uuid] = related_clusters[-1][1]
                continue

            related_cluster = cluster_dict[dest_uuid]

            self.statistics.public_relations_count += 1

            related_clusters.append((self, related_cluster, level))

            if (depth > 1 or depth == -1) and (
                cluster["dest-uuid"] not in visited
                or visited[cluster["dest-uuid"]] > level + 1
            ):
                new_depth = depth - 1 if depth > 1 else -1
                if cluster["dest-uuid"] in cluster_dict:
                    related_clusters += cluster_dict[
                        cluster["dest-uuid"]
                    ].get_related_clusters(
                        cluster_dict,
                        new_depth,
                        visited,
                        level + 1,
                        related_private_clusters,
                    )

        if empty_uuids > 0:
            self.statistics.empty_uuids_dict[self.value] = empty_uuids

        return self._remove_duplicates(related_clusters)
    
    def _remove_duplicates(self, related_clusters):
        cluster_dict = {}
        for cluster in related_clusters:
            key = tuple(sorted((cluster[0], cluster[1])))

            if key in cluster_dict:
                if cluster_dict[key][2] > cluster[2]:
                    cluster_dict[key] = cluster
            else:
                cluster_dict[key] = cluster
        related_clusters = list(cluster_dict.values())

        return related_clusters

    def _create_related_entry(self):
        self.entry += f"\n"
        self.entry += f'??? info "Related clusters"\n'
        self.entry += f"\n"
        self.entry += f"    To see the related clusters, click [here](./relations/{self.uuid}.md).\n"

    def _get_related_entry(self, relations):
        output = ""
        output += f"## Related clusters for {self.value}\n"
        output += f"\n"
        output += f"| Cluster A | Galaxy A | Cluster B | Galaxy B | Level {{ .graph }} |\n"
        output += f"|-----------|----------|-----------|----------|-------------------|\n"
        for relation in relations:
            placeholder = "__TMP__"

            cluster_a_section = (
                relation[0]
                .value.lower()
                .replace(" - ", placeholder)  # Replace " - " first
                .replace(" ", "-")
                .replace("/", "")
                .replace(":", "")
                .replace(placeholder, "-")
            )  # Replace the placeholder with "-"

            cluster_b_section = (
                relation[1]
                .value.lower()
                .replace(" - ", placeholder)  # Replace " - " first
                .replace(" ", "-")
                .replace("/", "")
                .replace(":", "")
                .replace(placeholder, "-")
            )  # Replace the placeholder with "-"

            if cluster_b_section != "private-cluster":
                output += f"| [{relation[0].value}  ({relation[0].uuid})](../../{relation[0].galaxy.json_file_name}/index.md#{cluster_a_section}) | [{relation[0].galaxy.name}](../../{relation[0].galaxy.json_file_name}/index.md) | [{relation[1].value}  ({relation[1].uuid})](../../{relation[1].galaxy.json_file_name}/index.md#{cluster_b_section}) |  [{relation[1].galaxy.name}](../../{relation[1].galaxy.json_file_name}/index.md) | {relation[2]} |\n"
            else:
                output += f"| [{relation[0].value}  ({relation[0].uuid})](../../{relation[0].galaxy.json_file_name}/index.md#{cluster_a_section}) | [{relation[0].galaxy.name}](../../{relation[0].galaxy.json_file_name}/index.md) |{relation[1].value}  ({relation[1].uuid}) | unknown | {relation[2]} |\n"
        return output

    def create_entry(self, cluster_dict, path):
        if not self.statistics:
            raise ValueError("Statistics not set")
        self._create_title_entry()
        self._create_description_entry()
        self._create_synonyms_entry()
        self._create_uuid_entry()
        self._create_refs_entry()
        self._create_associated_metadata_entry()
        if self.related_list:
            self._create_related_entry()
            self._write_relations(cluster_dict, path)
        return self.entry

    def _write_relations(self, cluster_dict, path):
        related_clusters = self.get_related_clusters(cluster_dict)
        self.statistics.relation_count_dict[self.uuid] = len(related_clusters)
        galaxy_path = os.path.join(path, self.galaxy.json_file_name)
        if not os.path.exists(galaxy_path):
            os.mkdir(galaxy_path)
        relation_path = os.path.join(galaxy_path, "relations")
        if not os.path.exists(relation_path):
            os.mkdir(relation_path)
        with open(os.path.join(relation_path, ".pages"), "w") as index:
            index.write(f"hide: true\n")
        with open(os.path.join(relation_path, f"{self.uuid}.md"), "w") as index:
            index.write(self._get_related_entry(related_clusters))
