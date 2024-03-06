from modules.galaxy import Galaxy
from modules.cluster import Cluster

from collections import defaultdict, deque


class Universe:
    def __init__(self, add_inbound_relationship=False):
        self.galaxies = {}  # Maps galaxy_name to Galaxy objects
        self.add_inbound_relationship = add_inbound_relationship
        self.private_clusters = {}

    def add_galaxy(self, galaxy_name, json_file_name, authors, description):
        if galaxy_name not in self.galaxies:
            self.galaxies[galaxy_name] = Galaxy(
                galaxy_name=galaxy_name,
                json_file_name=json_file_name,
                authors=authors,
                description=description,
            )

    def add_cluster(self, galaxy_name, uuid, description, value, meta):
        if galaxy_name in self.galaxies:
            self.galaxies[galaxy_name].add_cluster(
                uuid=uuid, description=description, value=value, meta=meta
            )

    def define_relationship(self, cluster_a_id, cluster_b_id):
        cluster_a = None
        cluster_b = None

        if cluster_a_id == cluster_b_id:
            return

        # Search for Cluster A and Cluster B in all galaxies
        for galaxy in self.galaxies.values():
            if cluster_a_id in galaxy.clusters:
                cluster_a = galaxy.clusters[cluster_a_id]
            if cluster_b_id in galaxy.clusters:
                cluster_b = galaxy.clusters[cluster_b_id]
            if cluster_a and cluster_b:
                break

        # If both clusters are found, define the relationship
        if cluster_a and cluster_b:
            cluster_a.add_outbound_relationship(cluster_b)
            cluster_b.add_inbound_relationship(cluster_a)
        else:
            if cluster_a:
                # private_cluster = self.add_cluster(uuid=cluster_b_id, galaxy_name="Unknown", description=None, value="Private Cluster", meta=None)
                private_cluster = Cluster(
                    uuid=cluster_b_id,
                    galaxy=None,
                    description=None,
                    value="Private Cluster",
                    meta=None,
                )
                self.private_clusters[cluster_b_id] = private_cluster
                cluster_a.add_outbound_relationship(private_cluster)
            else:
                raise ValueError(f"Cluster {cluster_a} not found in any galaxy")

    def get_relationships_with_levels(self, start_cluster):

        def bfs_with_undirected_relationships(start_cluster):
            visited = set()  # Tracks whether a cluster has been visited
            relationships = defaultdict(
                lambda: float("inf")
            )  # Tracks the lowest level for each cluster pair

            queue = deque([(start_cluster, 0)])  # Queue of (cluster, level)

            while queue:
                current_cluster, level = queue.popleft()
                if current_cluster not in visited:
                    visited.add(current_cluster)

                    # Process all relationships regardless of direction
                    if self.add_inbound_relationship:
                        neighbors = current_cluster.outbound_relationships.union(
                            current_cluster.inbound_relationships
                        )
                    else:
                        neighbors = current_cluster.outbound_relationships
                    for neighbor in neighbors:
                        link = frozenset([current_cluster, neighbor])
                        if level + 1 < relationships[link]:
                            relationships[link] = level + 1
                            if (
                                neighbor not in visited
                                and neighbor.value != "Private Cluster"
                            ):
                                queue.append((neighbor, level + 1))

            # Convert the defaultdict to a list of tuples, ignoring direction
            processed_relationships = []
            for link, lvl in relationships.items():
                # Extract clusters from the frozenset; direction is irrelevant
                clusters = list(link)

                # Arbitrarily choose the first cluster as 'source' for consistency
                if clusters[0].value == "Private Cluster":
                    processed_relationships.append((clusters[1], clusters[0], lvl))
                else:
                    processed_relationships.append((clusters[0], clusters[1], lvl))

            return processed_relationships

        return bfs_with_undirected_relationships(start_cluster)
