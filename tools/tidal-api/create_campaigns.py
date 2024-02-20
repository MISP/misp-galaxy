from api import TidalAPI
import json

VERSION = 1
GALAXY_PATH = "../../galaxies/"
CLUSTER_PATH = "../../clusters/"
GALAXY_UUID = "43a8fce6-08d3-46c2-957d-53606efe2c48"

def create_galaxy():
    galaxy = {}
    galaxy["description"] = "Tidal Campaigns Galaxy"
    galaxy["name"] = "Tidal Campaigns"
    galaxy["namespace"] = "tidal"
    galaxy["type"] = "campaigns"
    galaxy["uuid"] = GALAXY_UUID
    galaxy["version"] = VERSION
    return galaxy

def create_cluster(galaxy, data):
    cluster = {}
    values = []

    for campaigns in data["data"]:
        value = {}
        relations = []

        value["description"] = campaigns["description"]

        # Metadata fields
        source = campaigns["source"]
        campaign_attack_id = campaigns["campaign_attack_id"]
        first_seen = campaigns["first_seen"]
        last_seen = campaigns["last_seen"]
        tags = campaigns["tags"]
        owner = campaigns["owner_name"]

        value["meta"] = {}
        if source:
            value["meta"]["source"] = source
        if campaign_attack_id:
            value["meta"]["campaign-attack-id"] = campaign_attack_id
        if first_seen:
            value["meta"]["first-seen"] = first_seen
        if last_seen:
            value["meta"]["last-seen"] = last_seen
        if tags:
            value["meta"]["tags"] = tags
        if owner:
            value["meta"]["owner"] = owner

        value["related"] = relations
        value["uuid"] = campaigns["id"]
        value["value"] = campaigns["name"]
        values.append(value)

    cluster["authors"] = ["Tidal"]
    cluster["category"] = "Threat campaigns"
    cluster["description"] = "Tidal Campaigns"
    cluster["name"] = "Tidal Campaigns"
    cluster["source"] = "https://app-api.tidalcyber.com/api/v1/campaigns"
    cluster["type"] = "campaigns"
    cluster["uuid"] = galaxy["uuid"]
    cluster["values"] = values
    return cluster

if __name__ == "__main__":
    api = TidalAPI()
    data = api.get_data('campaigns')
    galaxy = create_galaxy()
    cluster = create_cluster(galaxy, data)

    with open(GALAXY_PATH + "tidal-campaigns.json", "w") as galaxy_file:
        json.dump(galaxy, galaxy_file, indent=4)

    with open(CLUSTER_PATH + "tidal-campaigns.json", "w") as cluster_file:
        json.dump(cluster, cluster_file, indent=4)
