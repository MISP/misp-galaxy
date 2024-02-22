import json

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return link_uuids(config)
    
def link_uuids(config):
    uuids = config["UUIDS"]
    for key, galaxy_config in config["GALAXY_CONFIGS"].items():
        galaxy_config["uuid"] = uuids[key]
    for key, cluster_config in config["CLUSTER_CONFIGS"].items():
        cluster_config["uuid"] = uuids[key]
    return config