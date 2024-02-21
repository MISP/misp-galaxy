from api import TidalAPI
import json
import re

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

        # Metadata fields
        links = extract_links(software["description"])
        source = software["source"]
        type = software["type"]
        software_attack_id = software["software_attack_id"]
        platforms = software["platforms"]
        tags = software["tags"]
        owner = software["owner_name"]

        value["meta"] = {}
        if links:
            value["meta"]["refs"] = list(links)
        if source:
            value["meta"]["source"] = source
        if type:
            value["meta"]["type"] = type
        if software_attack_id:
            value["meta"]["software-attack-id"] = software_attack_id
        if platforms:
            value["meta"]["platforms"] = platforms
        if tags:
            value["meta"]["tags"] = tags
        if owner:
            value["meta"]["owner"] = owner

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

def extract_links(text):
    # extract markdown links and return text without links and the links
    # urls = re.findall(r'https?://[^\s\)]+', text)
    regular_links = re.findall(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', text)
    # sup_links = re.findall(r'<sup>\[\[([^\]]+)\]\((https?://[^\s\)]+)\)\]</sup>', text)

    # Extracting URLs from the tuples
    regular_links_urls = set([url for text, url in regular_links])
    # sup_links_urls = [url for text, url in sup_links]

    # text_without_links = re.sub(r'\[([^\]]+)\]\(https?://[^\s\)]+\)', r'\1', text)
    # text_without_sup = re.sub(r'<sup>.*<\/sup>', '', text_without_links)

    return regular_links_urls

if __name__ == "__main__":
    api = TidalAPI()
    data = api.get_data('software')
    galaxy = create_galaxy()
    cluster = create_cluster(galaxy, data)

    with open(GALAXY_PATH + "tidal-software.json", "w") as galaxy_file:
        json.dump(galaxy, galaxy_file, indent=4)

    with open(CLUSTER_PATH + "tidal-software.json", "w") as cluster_file:
        json.dump(cluster, cluster_file, indent=4)