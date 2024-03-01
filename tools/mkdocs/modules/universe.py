from modules.galaxy import Galaxy
from modules.cluster import Cluster

from collections import defaultdict, deque


class Universe:
    def __init__(self):
        self.galaxies = {}  # Maps galaxy_name to Galaxy objects

    def add_galaxy(self, galaxy_name, json_file_name, authors, description):
        if galaxy_name not in self.galaxies:
            self.galaxies[galaxy_name] = Galaxy(galaxy_name=galaxy_name, json_file_name=json_file_name, authors=authors, description=description)

    def add_cluster(self, galaxy_name, uuid, description, value, meta):
        if galaxy_name in self.galaxies:
            self.galaxies[galaxy_name].add_cluster(uuid=uuid, description=description, value=value, meta=meta)

    def define_relationship(self, cluster_a_id, cluster_b_id):
        cluster_a = None
        cluster_b = None

        # Search for Cluster A and Cluster B in all galaxies
        for galaxy in self.galaxies.values():
            if cluster_a_id in galaxy.clusters:
                cluster_a = galaxy.clusters[cluster_a_id]
            if cluster_b_id in galaxy.clusters:
                cluster_b = galaxy.clusters[cluster_b_id]
            if cluster_a and cluster_b:  # Both clusters found
                break

        # If both clusters are found, define the relationship
        if cluster_a and cluster_b:
            cluster_a.add_outbound_relationship(cluster_b)
            cluster_b.add_inbound_relationship(cluster_a)
        else:
            # If Cluster B is not found, create a private cluster relationship for Cluster A
            if cluster_a:
                private_cluster = Cluster(uuid=cluster_b_id, galaxy=None)
                cluster_a.add_outbound_relationship(private_cluster)
            else:
                print("Cluster A not found in any galaxy")

    # def get_relationships_with_levels(self, galaxy, cluster):
    #     start_galaxy = self.galaxies[galaxy]
    #     start_cluster = start_galaxy.clusters[cluster]

    #     def bfs_with_inbound_outbound(start_cluster):
    #         visited = set()  # To keep track of visited clusters
    #         linked = set()  # To keep track of linked clusters
    #         queue = deque([(start_cluster, 0, 'outbound')])  # Include direction of relationship
    #         relationships = []

    #         while queue:
    #             current_cluster, level, direction = queue.popleft()
    #             if (current_cluster, direction) not in visited:  # Check visited with direction
    #                 visited.add((current_cluster, direction))

    #                 # Process outbound relationships
    #                 if direction == 'outbound':
    #                     for to_cluster in current_cluster.outbound_relationships:
    #                         if (to_cluster, 'outbound') not in visited:
    #                             # relationships.append((current_cluster, to_cluster, level + 1, 'outbound'))
    #                             queue.append((to_cluster, level + 1, 'outbound'))
    #                             relationships.append((current_cluster, to_cluster, level + 1, 'outbound'))
                            
                    
    #                 # Process inbound relationships
    #                 for from_cluster in current_cluster.inbound_relationships:
    #                     if (from_cluster, 'inbound') not in visited:
    #                         relationships.append((from_cluster, current_cluster, level + 1, 'inbound'))
    #                         queue.append((from_cluster, level + 1, 'inbound'))

    #         return relationships


    #     return bfs_with_inbound_outbound(start_cluster)

    # def get_relationships_with_levels(self, galaxy, cluster):
    #     start_galaxy = self.galaxies[galaxy]
    #     start_cluster = start_galaxy.clusters[cluster]

    #     def bfs_with_inbound_outbound(start_cluster):
    #         visited = set()  # To keep track of visited clusters
    #         relationships = defaultdict(lambda: (float('inf'), ''))  # Store lowest level for each link

    #         queue = deque([(start_cluster, 0, 'outbound')])  # Include direction of relationship

    #         while queue:
    #             print(f"Queue: {[c.uuid for c, l, d in queue]}")
    #             current_cluster, level, direction = queue.popleft()
    #             if (current_cluster, direction) not in visited:  # Check visited with direction
    #                 visited.add((current_cluster, direction))
                    
    #                 if current_cluster.uuid == "a5a067c9-c4d7-4f33-8e6f-01b903f89908":
    #                     print(f"Current cluster: {current_cluster.uuid}, Level: {level}, Direction: {direction}")
    #                     print(f"outbound relationships: {[x.uuid for x in current_cluster.outbound_relationships]}")


    #                 # Process outbound relationships
    #                 if direction == 'outbound':
    #                     for to_cluster in current_cluster.outbound_relationships:
    #                         if (to_cluster, 'outbound') not in visited:
    #                             queue.append((to_cluster, level + 1, 'outbound'))

    #                         link = frozenset([current_cluster, to_cluster])
    #                         if relationships[link][0] > level + 1:
    #                             relationships[link] = (level + 1, 'outbound')

    #                 # Process inbound relationships
    #                 for from_cluster in current_cluster.inbound_relationships:
    #                     if (from_cluster, 'inbound') not in visited:
    #                         queue.append((from_cluster, level + 1, 'inbound'))

    #                     link = frozenset([from_cluster, current_cluster])
    #                     if relationships[link][0] > level + 1:
    #                         relationships[link] = (level + 1, 'inbound')

    #         # Convert defaultdict to list of tuples for compatibility with your existing structure
    #         processed_relationships = []
    #         for link, (lvl, dir) in relationships.items():
    #             clusters = list(link)
    #             if dir == 'outbound':
    #                 processed_relationships.append((clusters[0], clusters[1], lvl, dir))
    #             else:
    #                 processed_relationships.append((clusters[1], clusters[0], lvl, dir))

    #         return processed_relationships

    #     return bfs_with_inbound_outbound(start_cluster)
    
    def get_relationships_with_levels(self, start_cluster):

        def bfs_with_undirected_relationships(start_cluster):
            visited = set()  # Tracks whether a cluster has been visited
            relationships = defaultdict(lambda: float('inf'))  # Tracks the lowest level for each cluster pair

            queue = deque([(start_cluster, 0)])  # Queue of (cluster, level)

            while queue:
                current_cluster, level = queue.popleft()
                if current_cluster not in visited:
                    visited.add(current_cluster)

                    # Process all relationships regardless of direction
                    neighbors = current_cluster.outbound_relationships.union(current_cluster.inbound_relationships)
                    for neighbor in neighbors:
                        link = frozenset([current_cluster, neighbor])
                        if level + 1 < relationships[link]:
                            relationships[link] = level + 1
                            if neighbor not in visited:
                                queue.append((neighbor, level + 1))

            # Convert the defaultdict to a list of tuples, ignoring direction
            processed_relationships = []
            for link, lvl in relationships.items():
                # Extract clusters from the frozenset; direction is irrelevant
                clusters = list(link)
                
                # Arbitrarily choose the first cluster as 'source' for consistency
                try: 
                    processed_relationships.append((clusters[0], clusters[1], lvl))
                except:
                    processed_relationships.append((clusters[0], Cluster(uuid=0, galaxy=None), lvl))

            return processed_relationships

        return bfs_with_undirected_relationships(start_cluster)