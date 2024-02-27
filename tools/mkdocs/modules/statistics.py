from utils.helper import get_top_x, name_to_section
import os


class Statistics:
    def __init__(self, cluster_dict):
        self.public_relations_count = 0
        self.private_relations_count = 0
        self.private_clusters = []
        self.public_clusters_dict = {}
        self.relation_count_dict = {}
        self.synonyms_count_dict = {}
        self.empty_uuids_dict = {}
        self.cluster_dict = cluster_dict
        self.entry = ""

    def create_entry(self):
        self.entry += f"# MISP Galaxy statistics\n"
        self.entry += "The MISP galaxy statistics are automatically generated based on the MISP galaxy JSON files. Therefore the statistics only include detailed infomration about public clusters and relations. Some statistics about private clusters and relations is included but only as an approximation based on the information gathered from the public clusters.\n"
        self.entry += "\n"
        self._create_cluster_statistics()
        self._create_galaxy_statistics()
        self._create_relation_statistics()
        self._create_synonym_statistics()

    def _create_galaxy_statistics(self):
        self.entry += f"# Galaxy statistics\n"
        self.entry += f"## Galaxies with the most clusters\n"
        galaxy_counts = {}
        for galaxy in self.public_clusters_dict.values():
            galaxy_counts[galaxy] = galaxy_counts.get(galaxy, 0) + 1
        top_galaxies, top_galaxies_values = get_top_x(galaxy_counts, 20)
        self.entry += f" | No. | Galaxy | Count {{ .log-bar-chart }}|\n"
        self.entry += f" |----|--------|-------|\n"
        for i, galaxy in enumerate(top_galaxies, 1):
            galaxy_section = name_to_section(galaxy.json_file_name)
            self.entry += f" | {i} | [{galaxy.name}](../{galaxy_section}) | {top_galaxies_values[i-1]} |\n"
        self.entry += f"\n"

        self.entry += f"## Galaxies with the least clusters\n"
        flop_galaxies, flop_galaxies_values = get_top_x(galaxy_counts, 20, False)
        self.entry += f" | No. | Galaxy | Count {{ .bar-chart }}|\n"
        self.entry += f" |----|--------|-------|\n"
        for i, galaxy in enumerate(flop_galaxies, 1):
            galaxy_section = name_to_section(galaxy.json_file_name)
            self.entry += f" | {i} | [{galaxy.name}](../{galaxy_section}) | {flop_galaxies_values[i-1]} |\n"
        self.entry += f"\n"

    def _create_cluster_statistics(self):
        self.entry += f"# Cluster statistics\n"
        self.entry += f"## Number of clusters\n"
        self.entry += f"Here you can find the total number of clusters including public and private clusters. The number of public clusters has been calculated based on the number of unique Clusters in the MISP galaxy JSON files. The number of private clusters could only be approximated based on the number of relations to non-existing clusters. Therefore the number of private clusters is not accurate and only an approximation.\n"
        self.entry += f"\n"
        self.entry += f"| No. | Type | Count {{ .pie-chart }}|\n"
        self.entry += f"|-----|------|-----------------------|\n"
        self.entry += f"| 1 | Public clusters | {len(self.public_clusters_dict)} |\n"
        self.entry += f"| 2 | Private clusters | {len(self.private_clusters)} |\n"
        self.entry += f"\n"

    def _create_relation_statistics(self):
        self.entry += f"# Relation statistics\n"
        self.entry += f"Here you can find the total number of relations including public and private relations. The number includes relations between public clusters and relations between public and private clusters. Therefore relatons between private clusters are not included in the statistics.\n"
        self.entry += f"\n"
        self.entry += f"## Number of relations\n"
        self.entry += f"| No. | Type | Count {{ .pie-chart }}|\n"
        self.entry += f"|----|------|-------|\n"
        self.entry += f"| 1 | Public relations | {self.public_relations_count} |\n"
        self.entry += f"| 2 | Private relations | {self.private_relations_count} |\n"
        self.entry += f"\n"

        self.entry += f"**Average number of relations per cluster**: {int(sum(self.relation_count_dict.values()) / len(self.relation_count_dict))}\n"

        self.entry += f"## Cluster with the most relations\n"
        relation_count_dict_names = {
            self.cluster_dict[uuid].value: count
            for uuid, count in self.relation_count_dict.items()
        }
        top_25_relation, top_25_relation_values = get_top_x(
            relation_count_dict_names, 20
        )
        self.entry += f" | No. | Cluster | Count {{ .bar-chart }}|\n"
        self.entry += f" |----|--------|-------|\n"
        relation_count_dict_galaxies = {
            self.cluster_dict[uuid].value: self.cluster_dict[uuid].galaxy.json_file_name
            for uuid in self.relation_count_dict.keys()
        }
        for i, cluster in enumerate(top_25_relation, 1):
            cluster_section = name_to_section(cluster)
            self.entry += f" | {i} | [{cluster}](../{relation_count_dict_galaxies[cluster]}/#{cluster_section}) | {top_25_relation_values[i-1]} |\n"
        self.entry += f"\n"

    def _create_synonym_statistics(self):
        self.entry += f"# Synonym statistics\n"
        self.entry += f"## Cluster with the most synonyms\n"
        synonyms_count_dict_names = {
            self.cluster_dict[uuid].value: count
            for uuid, count in self.synonyms_count_dict.items()
        }
        top_synonyms, top_synonyms_values = get_top_x(synonyms_count_dict_names, 20)
        self.entry += f" | No. | Cluster | Count {{ .bar-chart }}|\n"
        self.entry += f" |----|--------|-------|\n"
        synonyms_count_dict_galaxies = {
            self.cluster_dict[uuid].value: self.cluster_dict[uuid].galaxy.json_file_name
            for uuid in self.synonyms_count_dict.keys()
        }
        for i, cluster in enumerate(top_synonyms, 1):
            cluster_section = name_to_section(cluster)
            self.entry += f" | {i} | [{cluster}](../{synonyms_count_dict_galaxies[cluster]}/#{cluster_section}) | {top_synonyms_values[i-1]} |\n"
        self.entry += f"\n"

    def write_entry(self, path):
        self.create_entry()
        with open(os.path.join(path, "statistics.md"), "w") as index:
            index.write(self.entry)

    def add_cluster(self, cluster):
        self.public_clusters_dict[cluster.uuid] = cluster.galaxy
        cluster.statistics = self
