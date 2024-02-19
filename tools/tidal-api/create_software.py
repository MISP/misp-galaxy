from api import TidalAPI
import json

VERSION = 1
GALAXY_PATH = "../../galaxies/"
CLUSTER_PATH = "../../clusters/"
GALAXY_UUID = "38d62d8b-4c49-489a-9bc4-8e294c4f04f7"

def create_galaxy():
    galaxy = {}
    galaxy["description"] = "Tidal Software Galaxy"
    galaxy["name"] = "Tidal Software"
    galaxy["namespace"] = "tidal"
    galaxy["type"] = "software"
    galaxy["uuid"] = GALAXY_UUID
    galaxy["version"] = VERSION
    return galaxy

def create_cluster(galaxy, data):
    cluster = {}
    values = []

    for software in data["data"]:
        value = {}
        relations = []
        # TODO check for relations etc.
        for entry in software["groups"]:
            relation = {}
            relation["dest-uuid"] = entry["id"]
            relation["type"] = "used-by"
            relations.append(relation)
        for entry in software["associated_software"]:
            relation = {}
            relation["dest-uuid"] = entry["id"]
            relation["type"] = "related-to"
            relations.append(relation)

        value["description"] = software["description"]

        value["meta"] = {}
        value["meta"]["source"] = software["source"]
        value["meta"]["type"] = software["type"]
        value["meta"]["software-attack-id"] = software["software_attack_id"]
        value["meta"]["platforms"] = software["platforms"]
        value["meta"]["tags"] = software["tags"]
        value["meta"]["owner"] = software["owner_name"]

        value["related"] = relations
        value["uuid"] = software["id"]
        value["value"] = software["name"]
        values.append(value)

    cluster["authors"] = ["Tidal"]
    cluster["category"] = "Threat software"
    cluster["description"] = "Tidal Threat Groups"
    cluster["name"] = "Tidal Threat software"
    cluster["source"] = "https://app-api.tidalcyber.com/api/v1/software"
    cluster["type"] = "threat-software"
    cluster["uuid"] = galaxy["uuid"]
    cluster["values"] = values
    return cluster

if __name__ == "__main__":
    api = TidalAPI()
    data = api.get_data('software')
    galaxy = create_galaxy()
    cluster = create_cluster(galaxy, data)

    with open(GALAXY_PATH + "tidal-software.json", "w") as galaxy_file:
        json.dump(galaxy, galaxy_file, indent=4)

    with open(CLUSTER_PATH + "tidal-software.json", "w") as cluster_file:
        json.dump(cluster, cluster_file, indent=4)