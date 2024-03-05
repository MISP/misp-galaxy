from api.api import TidalAPI
from models.galaxy import Galaxy
from models.cluster import (
    GroupCluster,
    SoftwareCluster,
    CampaignsCluster,
    TechniqueCluster,
    TacticCluster,
    ReferencesCluster,
)
import argparse
import json
import os

CONFIG = "./config"
GALAXY_PATH = "../../galaxies"
CLUSTER_PATH = "../../clusters"


def create_galaxy(
    endpoint: str,
    version: int,
    extended_relations: bool = False,
    create_subs: bool = False,
):
    api = TidalAPI()
    data = api.get_data(endpoint)
    with open(f"{CONFIG}/{endpoint}.json", "r") as file:
        config = json.load(file)

    galaxy = Galaxy(**config["galaxy"], version=version)
    galaxy.save_to_file(f"{GALAXY_PATH}/tidal-{endpoint}.json")

    match endpoint:
        case "groups":
            cluster = GroupCluster(
                **config["cluster"],
                uuid=galaxy.uuid,
                enrichment=extended_relations,
                subs=create_subs,
                version=version,
            )
            cluster.add_values(data)
        case "software":
            cluster = SoftwareCluster(
                **config["cluster"],
                uuid=galaxy.uuid,
                version=version,
                enrichment=extended_relations,
                subs=create_subs,
            )
            cluster.add_values(data)
        case "campaigns":
            cluster = CampaignsCluster(**config["cluster"], uuid=galaxy.uuid, version=version)
            cluster.add_values(data)
        case "technique":
            cluster = TechniqueCluster(
                **config["cluster"], uuid=galaxy.uuid, subs=create_subs, version=version
            )
            cluster.add_values(data)
        case "tactic":
            cluster = TacticCluster(**config["cluster"], uuid=galaxy.uuid, version=version)
            cluster.add_values(data)
        case "references":
            cluster = ReferencesCluster(**config["cluster"], uuid=galaxy.uuid, version=version)
            cluster.add_values(data)
        case _:
            print("Error: Invalid endpoint")
            return

    cluster.save_to_file(f"{CLUSTER_PATH}/tidal-{endpoint}.json")
    print(f"Galaxy tidal-{endpoint} created")


def main(args, galaxies):
    if args.all:
        for galaxy in galaxies:
            create_galaxy(
                galaxy, args.version, args.extended_relations, args.create_subs
            )
    else:
        create_galaxy(
            args.type, args.version, args.extended_relations, args.create_subs
        )


if __name__ == "__main__":

    galaxies = []
    for f in os.listdir(CONFIG):
        if f.endswith(".json"):
            galaxies.append(f.split(".")[0])

    parser = argparse.ArgumentParser(
        description="Create galaxy and cluster json files from Tidal API"
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Create all galaxies and clusters",
    )
    parser.add_argument(
        "--type",
        choices=galaxies,
        help="The type of the file to create",
    )
    parser.add_argument(
        "-v",
        "--version",
        type=int,
        required=True,
        help="The version of the galaxy",
    )
    parser.add_argument(
        "--extended-relations",
        action="store_true",
        help="Create extended relations for the clusters",
    )
    parser.add_argument(
        "--create-subs",
        action="store_true",
        help="Create subclusters from the API",
    )
    parser.set_defaults(func=main)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args, galaxies=galaxies)
    else:
        parser.print_help()
