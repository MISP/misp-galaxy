from api.api import TidalAPI
from models.galaxy import Galaxy
from models.cluster import Cluster
from utils.extractor import extract_links
import argparse

CLUSTER_PATH = "../../clusters/"
GALAXY_PATH = "../../galaxies/"

UUIDS = {
    "software": "38d62d8b-4c49-489a-9bc4-8e294c4f04f7",
    "groups": "41c3e5c0-de5c-4edb-b48b-48cd8e7519e6",
    "campaigns": "43a8fce6-08d3-46c2-957d-53606efe2c48",
}

GALAXY_CONFIGS = {
    "software": {
        "name": "Tidal Software",
        "namespace": "tidal",
        "description": "Tidal Software Galaxy",
        "type": "software",
        "uuid": UUIDS["software"],
    },
    "groups": {
        "name": "Tidal Groups",
        "namespace": "tidal",
        "description": "Tidal Groups Galaxy",
        "type": "groups",
        "uuid": UUIDS["groups"],
    },
    "campaigns": {
        "name": "Tidal Campaigns",
        "namespace": "tidal",
        "description": "Tidal Campaigns Galaxy",
        "type": "campaigns",
        "uuid": UUIDS["campaigns"],
    }
}

CLUSTER_CONFIGS = {
    "software": {
        "authors": "Tidal",
        "category": "Software",
        "description": "Tidal Software Cluster",
        "name": "Tidal Software",
        "source": "Tidal",
        "type": "software",
        "uuid": UUIDS["software"],
        "values": []
    },
    "groups": {
        "authors": "Tidal",
        "category": "Threat Groups",
        "description": "Tidal Threat Groups Cluster",
        "name": "Tidal Threat Groups",
        "source": "Tidal",
        "type": "groups",
        "uuid": UUIDS["groups"],
        "values": []
    },
    "campaigns": {
        "authors": "Tidal",
        "category": "Campaigns",
        "description": "Tidal Campaigns Cluster",
        "name": "Tidal Campaigns",
        "source": "Tidal",
        "type": "campaigns",
        "uuid": UUIDS["campaigns"],
        "values": []
    }
}

VALUE_FIELDS = {
    "software": {
        "description": "description",
        "meta": {
            "source": "source",
            "type": "type",
            "software-attack-id": "software_attack_id",
            "platforms": "platforms",
            "tags": "tags",
            "owner": "owner_name"
        },
        "related": {
            "groups": {
                "dest-uuid": "group_id",
                "type": "used-by"
            },
            "associated_software": {
                "dest-uuid": "id",
                "type": "related-to"
            }
        },
        "uuid": "id",
        "value": "name"
    },
    "groups": {
        "description": "description",
        "meta": {
            "source": "source",
            "group-attack-id": "group_attack_id",
            "country": {"extract": "single", "key": "country", "subkey": "country_code"},
            "observed_country": {"extract": "multiple", "key": "observed_country", "subkey": "country_code"},
            "observed_motivation": {"extract": "multiple", "key": "observed_motivation", "subkey": "name"},
            "target-category": {"extract": "multiple", "key": "observed_sector", "subkey": "name"},
            "tags": "tags",
            "owner": "owner_name"
        },
        "related": {
            "associated_groups": {
                "dest-uuid": "id",
                "type": "related-to"
            }
        },
        "uuid": "id",
        "value": "name"
    },
    "campaigns": {
        "description": "description",
        "meta": {
            "source": "source",
            "campaign-attack-id": "campaign_attack_id",
            "first_seen": "first_seen",
            "last_seen": "last_seen",
            "tags": "tags",
            "owner": "owner_name"
        },
        "related": {},
        "uuid": "id",
        "value": "name"
    }
    
}

def create_cluster_values(data, cluster):
    value_fields = VALUE_FIELDS[cluster.internal_type]
    for entry in data["data"]:
        values = {}
        for key, value in value_fields.items():
            match key:
                case "description":
                    values[value] = entry.get(key)
                case "meta":
                    metadata = create_metadata(entry, value)
                    values["meta"] = metadata
                case "related":
                    relations = create_relations(entry, value)
                    values["related"] = relations
                case "uuid":
                    values[key] = entry.get(value)
                case "value":
                    values[key] = entry.get(value)
                case _:
                    print(f"Error: Invalid configuration for {key} in {cluster.internal_type} value fields.")
        cluster.add_value(values)

def create_metadata(data, format):
    metadata = {}
    for meta_key, meta_value in format.items():
        if isinstance(meta_value, dict):
            if meta_value.get("extract") == "single" and data.get(meta_value["key"]):
                metadata[meta_key] = data.get(meta_value["key"])[0].get(meta_value["subkey"])
            elif meta_value.get("extract") == "multiple" and data.get(meta_value["key"]):
                metadata[meta_key] = [entry.get(meta_value["subkey"]) for entry in data.get(meta_value["key"])]
        elif data.get(meta_value):
            metadata[meta_key] = data.get(meta_value)
    return metadata
    

def create_relations(data, format):
    relations = []
    for i in range(len(list(format))):
        for relation in data[list(format)[i]]:
            relation_entry = {}
            for relation_key, relation_value in list(format.values())[i].items():
                if relation_key != "type":
                    relation_entry[relation_key] = relation.get(relation_value)
                else:
                    relation_entry[relation_key] = relation_value
            relations.append(relation_entry)
    return relations
    

def create_galaxy_and_cluster(galaxy_type, version):
    api = TidalAPI()
    galaxy = Galaxy(**GALAXY_CONFIGS[galaxy_type], version=version)
    galaxy.save_to_file(f"{GALAXY_PATH}/tidal-{galaxy_type}.json")

    cluster = Cluster(**CLUSTER_CONFIGS[galaxy_type], internal_type=galaxy_type)
    data = api.get_data(galaxy_type)
    create_cluster_values(data, cluster)
    cluster.save_to_file(f"{CLUSTER_PATH}/tidal-{galaxy_type}.json")

    print(f"Galaxy {galaxy_type} created")

def create_galaxy(args):
    if args.all:
        for galaxy_type in GALAXY_CONFIGS:
            create_galaxy_and_cluster(galaxy_type, args.version)
    else:
        create_galaxy_and_cluster(args.type, args.version)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a galaxy and cluster for Tidal API")
    subparsers = parser.add_subparsers(dest="command")

    galaxy_parser = subparsers.add_parser("create_galaxy", help="Create a galaxy from the Tidal API")
    galaxy_parser.add_argument("--type", choices=list(GALAXY_CONFIGS.keys()) + ['all'], help="The type of the galaxy")
    galaxy_parser.add_argument("-v", "--version", type=int, required=True, help="The version of the galaxy")
    galaxy_parser.add_argument("--all", action="store_true", help="Flag to create all predefined galaxy types")
    galaxy_parser.set_defaults(func=create_galaxy)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

