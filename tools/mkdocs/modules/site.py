import os

from utils.helper import create_bar_chart, get_top_x, create_pie_chart


class Site:
    def __init__(self, path, name) -> None:
        self.path = path
        self.name = name
        self.content = '[Hide Navigation](#){ .md-button #toggle-navigation }\n[Hide TOC](#){ .md-button #toggle-toc }\n<div class="clearfix"></div> \n\n'

    def add_content(self, content):
        self.content += content

    def write_entry(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        with open(os.path.join(self.path, self.name), "w") as index:
            index.write(self.content)


class IndexSite(Site):
    def __init__(self, path) -> None:
        super().__init__(path=path, name="index.md")

    def add_toc(self, galaxies):
        for galaxy in galaxies:
            galaxy_folder = galaxy.json_file_name.replace(".json", "")
            self.add_content(f"- [{galaxy.galaxy_name}](./{galaxy_folder}/index.md)\n")
            self.add_content("\n")


class StatisticsSite(Site):
    def __init__(self, path) -> None:
        super().__init__(path=path, name="statistics.md")

    def add_galaxy_statistics(self, galaxies):
        galaxy_cluster_count = {galaxy: len(galaxy.clusters) for galaxy in galaxies}
        top_20 = get_top_x(galaxy_cluster_count, 20)
        flop_20 = get_top_x(galaxy_cluster_count, 20, False)
        self.add_content(f"# Galaxy statistics\n")
        self.add_content(f"## Galaxies with the most clusters\n\n")
        self.add_content(
            create_bar_chart(
                x_axis="Galaxy", y_axis="Count", values=top_20, galaxy=True
            )
        )
        self.add_content(f"## Galaxies with the least clusters\n\n")
        self.add_content(
            create_bar_chart(
                x_axis="Galaxy", y_axis="Count", values=flop_20, galaxy=True
            )
        )

    def add_cluster_statistics(self, public_clusters, private_clusters):
        values = {
            "Public clusters": public_clusters,
            "Private clusters": private_clusters,
        }
        self.add_content(f"# Cluster statistics\n")
        self.add_content(f"## Number of clusters\n")
        self.add_content(
            f"Here you can find the total number of clusters including public and private clusters.The number of public clusters has been calculated based on the number of unique Clusters in the MISP galaxy JSON files. The number of private clusters could only be approximated based on the number of relations to non-existing clusters. Therefore the number of private clusters is not accurate and only an approximation.\n\n"
        )
        self.add_content(create_pie_chart(sector="Type", unit="Count", values=values))

    def add_relation_statistics(self, clusters):
        cluster_relations = {}
        private_relations = 0
        public_relations = 0
        for cluster in clusters:
            cluster_relations[cluster] = len(cluster.relationships)
            for relation in cluster.relationships:
                if relation[1].value == "Private Cluster":
                    private_relations += 1
                else:
                    public_relations += 1
        top_20 = get_top_x(cluster_relations, 20)
        flop_20 = get_top_x(cluster_relations, 20, False)
        self.add_content(f"# Relation statistics\n")
        self.add_content(
            f"Here you can find the total number of relations including public and private relations. The number includes relations between public clusters and relations between public and private clusters. Therefore relatons between private clusters are not included in the statistics.\n\n"
        )
        self.add_content(f"## Number of relations\n\n")
        self.add_content(
            create_pie_chart(
                sector="Type",
                unit="Count",
                values={
                    "Public relations": public_relations,
                    "Private relations": private_relations,
                },
            )
        )
        self.add_content(
            f"**Average number of relations per cluster**: {int(sum(cluster_relations.values()) / len(cluster_relations))}\n"
        )
        self.add_content(f"## Cluster with the most relations\n\n")
        self.add_content(
            create_bar_chart(x_axis="Cluster", y_axis="Count", values=top_20)
        )
        self.add_content(f"## Cluster with the least relations\n\n")
        self.add_content(
            create_bar_chart(x_axis="Cluster", y_axis="Count", values=flop_20)
        )

    def add_synonym_statistics(self, clusters):
        synonyms = {}
        for cluster in clusters:
            if cluster.meta and cluster.meta.get("synonyms"):
                synonyms[cluster] = len(cluster.meta["synonyms"])
        top_20 = get_top_x(synonyms, 20)
        self.add_content(f"# Synonym statistics\n")
        self.add_content(f"## Cluster with the most synonyms\n\n")
        self.add_content(
            create_bar_chart(x_axis="Cluster", y_axis="Count", values=top_20)
        )
