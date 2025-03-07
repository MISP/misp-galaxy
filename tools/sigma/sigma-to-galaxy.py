"""

        Author:         Jose Luis Sanchez Martinez
        Twitter:        @Joseliyo_Jstnk
        date:           2022/11/18
        Modified:       2023/01/03
        GitHub:         https://github.com/jstnk9/MISP
        Description:    This script can create MISP Galaxies from Sigma Rules. It can be done setting the path
                        where you have stored your sigma rules in the system.
        Examples:       python sigma-to-galaxy -p "C:\lab\sigma\rules\" -r
        MISP Galaxy:    https://github.com/MISP/misp-galaxy

"""

import os, json, yaml, argparse, uuid, configparser, time

unique_uuid = '9cf7cd2e-d5f1-48c4-9909-7896ba1c96b2'


def main(args):
    uuidGalaxy = create_galaxy_json()
    galaxyCluster = create_cluster(uuidGalaxy=unique_uuid)
    valuesData = create_cluster_value(args.inputPath, args.recursive, galaxyCluster)
    galaxyCluster["values"].extend(valuesData)
    galaxyCluster = createRelations(galaxyCluster)
    create_cluster_json(galaxyCluster)
    check_duplicates(galaxyCluster)


def createRelations(galaxyCluster):
    """
    :param galaxyCluster: Content of the cluster with all the values related to the Sigma Rules

    :return galaxyCluster: Content of the cluster adding the relation between sigma rule and MITRE technique
    """
    for obj in galaxyCluster["values"]:
        for attack in obj["meta"]["tags"]:
            if attack.startswith("attack.t"):
                with open(
                    config["MISP"]["cluster_path"]
                    + config["MISP"]["mitre_attack_cluster"],
                    "r",
                ) as mitreCluster:
                    data = json.load(mitreCluster)
                    for technique in data["values"]:
                        if (
                            technique["meta"]["external_id"]
                            == attack.split(".", 1)[1].upper()
                        ):
                            if obj.get("related"):
                                obj["related"].append(
                                    {
                                        "dest-uuid": "%s" % (technique["uuid"]),
                                        "tags": [
                                            "estimative-language:likelihood-probability=\"almost-certain\""
                                        ],
                                        "type": "related-to",
                                    }
                                )
                            else:
                                obj["related"] = []
                                obj["related"].append(
                                    {
                                        "dest-uuid": "%s" % (technique["uuid"]),
                                        "tags": [
                                            "estimative-language:likelihood-probability=\"almost-certain\""
                                        ],
                                        "type": "related-to",
                                    }
                                )

    return galaxyCluster


def check_duplicates(galaxy):
    """
    :param galaxy: Content of the cluster with all the values

    :return res:
    """
    galaxiesObj = {}
    for val in galaxy["values"]:
        obj = {}
        if galaxiesObj.get(val["value"]):
            galaxiesObj[val["value"]].append(val["uuid"])
        else:
            galaxiesObj[val["value"]] = []
            galaxiesObj[val["value"]].append(val["uuid"])

    for k, v in galaxiesObj.items():
        if len(v) > 1:
            print("[*] Title duplicated: %s " % (k))
            for ids in v:
                print("   %s" % (ids))


def create_cluster_json(galaxyCluster):
    """
    :param galaxyCluster: Content of the cluster with all the values related to the Sigma Rules

    This function finally creates the sigma-cluster.json file with all the information.
    """
    with open("sigma-cluster.json", "w") as f:
        json.dump(galaxyCluster, f, default=str)


def parseYaml(inputPath, yamlFile):
    """
    :param inputPath: Path where is stored the Sigma Rule to parse.
    :param yamlFile: Content of the Sigma Rule.

    This function can convert a Sigma Rule to JSON (dict)

    :return jsonData: Sigma rule converted to dict.
    """
    fullPath = os.path.join(inputPath, yamlFile)
    with open(fullPath, encoding='utf-8') as f:
        jsonData = yaml.load(f, Loader=yaml.FullLoader)
    return jsonData


def create_cluster(uuidGalaxy=unique_uuid):
    """
    :param uuidGalaxy: Is the uuid4 generated for the galaxy JSON file previously.

    This function creates the JSON file of the path /app/files/misp-galaxy/clusters without values.

    :return cluster: Dict with the basic information needed for the JSON file.
    """
    version = int(time.strftime("%Y%m%d"))
    cluster = {
        "authors": ["@Joseliyo_Jstnk"],
        "category": "rules",
        "description": "MISP galaxy cluster based on Sigma Rules.",
        "name": "Sigma-Rules",
        "source": "https://github.com/jstnk9/MISP/tree/main/misp-galaxy/sigma",
        "type": "sigma-rules",
        "uuid": uuidGalaxy,
        "values": [],
        "version": version
    }

    return cluster


def create_cluster_value(pathsigma, recursive, galaxyCluster):
    """
    :param pathsigma: Is the path established with the -p parameter
    :param recurisve: If true, it can recursively navigate through every subfolder of :pathsigma:
    :param galaxyCluster: Dictionary with the information needed for the cluster JSON file

    This function makes a loop in every subfolder to identify Sigma Rules and after that..
    1. It parse the YAML file to dict
    2. Once it's a dict, it call the function to parse the dict and start creating the
    values of the cluster

    IMPORTANT: Sigma rules must ends with .yml and not .yaml

    :return valuesData: Array with every Sigma Rule parsed into a dict.
    """
    valuesData = []
    if recursive == True:
        for dirpath, dirs, files in os.walk(pathsigma):
            if os.name == 'nt':
                path = dirpath.split('/')[0]
            else:
                path = dirpath

            for f in files:
                if f.endswith(".yml"):
                    jsonData = parseYaml(path, f)
                    valuesData.append(
                        parse_sigma_to_cluster(jsonData, f, path.split("rules")[1])
                    )

    return valuesData


def parse_sigma_to_cluster(jsonData, sigmaFile, sigmaPath):
    """
    :param jsonData: Is the Sigma Rule parsed to dict.
    :param sigmaFile: Is the Sigma Rule filename.
    :param sigmaPath: Is the path where are stored the Sigma Rules.

    This function parse the dict of the Sigma Rule to fill all the fields needed for the MISP Galaxy.

    :return valueData: Dict with all the fields filled ready to be added in the cluster JSON file.

    """
    valueData = {}
    valueData["description"] = jsonData.get("description", "No established description")
    valueData["uuid"] = jsonData.get("id", "No established id")
    valueData["value"] = jsonData.get("title", "No established title")
    valueData["meta"] = {}
    valueData["meta"]["refs"] = []
    if jsonData.get("references"):
        for rf in jsonData.get("references"):
            valueData["meta"]["refs"].append(rf)
        valueData["meta"]["refs"] = [
            *set(valueData["meta"]["refs"])
        ]  # Removing duplicated references
    valueData["meta"]["tags"] = jsonData.get("tags", "No established tags")
    valueData["meta"]["creation_date"] = jsonData.get("date", "No established date")
    valueData["meta"]["filename"] = sigmaFile
    valueData["meta"]["author"] = jsonData.get("author", "No established author")
    valueData["meta"]["level"] = jsonData.get("level", "No established level")
    valueData["meta"]["falsepositive"] = jsonData.get(
        "falsepositives", "No established falsepositives"
    )
    valueData["meta"]["refs"].append(
        "https://github.com/SigmaHQ/sigma/tree/master/rules%s/%s"
        % (sigmaPath.replace("\\", "/"), sigmaFile)
    )  # this value only works if you set the path like it was cloned from github
    valueData["meta"]["logsource.category"] = jsonData.get("logsource").get(
        "category", "No established category"
    )
    valueData["meta"]["logsource.product"] = jsonData.get("logsource").get(
        "product", "No established product"
    )
    return valueData


def create_galaxy_json():
    """
    This method creates first the galaxy JSON stored in the path /app/files/misp-galaxy/galaxies
    The information of this JSON is basic.

    :return uuidGalaxy: Return the uuid needed for the cluster JSON File which is created after this.
    """
    uuidGalaxy = unique_uuid
    galaxy = {
        "description": "Sigma Rules are used to detect suspicious behaviors related to threat actors, malware and tools",
        "icon": "link",
        "name": "Sigma-Rules",
        "namespace": "misp",
        "type": "sigma-rules",
        "uuid": uuidGalaxy,
        "version": 1,
    }
    with open("sigma-rules.json", "w") as f:
        json.dump(galaxy, f)

    return uuidGalaxy


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("config.ini")
    parser = argparse.ArgumentParser(
        description="This script can convert your sigma rules in MISP galaxies, generating both files needed for cluster and galaxies. If you need more information about how to import it, please, go to https://github.com/jstnk9/MISP/tree/main/misp-galaxy/sigma"
    )
    parser.add_argument(
        "-p",
        "--path",
        dest="inputPath",
        required=True,
        default="None",
        help="Path with your sigma rules.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        dest="recursive",
        action="store_true",
        help="If you have subfolders on the initial path and you want to convert all of them, use -r to do it recursive.",
    )
    args = parser.parse_args()
    main(args)
