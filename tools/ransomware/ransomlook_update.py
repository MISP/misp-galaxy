import requests
import json
import time
import uuid
import re
from pathlib import Path

# open clusters/ransomware
ransompath = Path(__file__).parent.parent.parent / 'clusters' / 'ransomware.json'
ransomware_galaxy = ransompath.open("r")
ransom_galaxy = json.load(ransomware_galaxy)
ransomware_galaxy.close()

# get groups names from ransomlook
ransomlook_groups = requests.get("https://www.ransomlook.io/api/groups")
ransomlook_groups = ransomlook_groups.json()

# tracking updated and created clusters
updated = []
created = []

# preparing name groups exception management
# For now, only seen exceptions are groups with a known synonym in parentheses
# ex: "Eraleign (Apt73)"
exceptions = []

pattern = re.compile(r'^(.*)\((.*)\)$')

for rlookgroup in ransomlook_groups:
    match = pattern.match(rlookgroup)
    if match:
        # Name as registred in ransomlook, first known name, synonym
        exceptions.append((rlookgroup, match.group(1).strip(), match.group(2).strip()))

for rlookgroup in ransomlook_groups:
    # check if it is an exception
    true_rlookgroup = rlookgroup
    synonym = ""
    if exceptions:
        for exception in exceptions:
            if rlookgroup.lower() == exception[0].lower():
                rlookgroup = exception[1]
                synonym = exception[2]
                break

    # get data from ransomlook
    ransom_data = requests.get(
        "https://www.ransomlook.io/api/group/" + str(true_rlookgroup)
    ).json()

    # checking if the cluster exists
    cluster_exist = False
    for cluster in ransom_galaxy['values']:
        if cluster['value'].lower() == rlookgroup.lower():
            cluster_exist = True
        elif 'meta' in cluster:
            if 'synonyms' in cluster['meta']:
                for syn in cluster['meta']['synonyms']:
                    if syn.lower() == rlookgroup.lower():
                        cluster_exist = True

        # Updating the cluster if existing
        if cluster_exist == True:
            if 'description' not in cluster:
                if ransom_data[0]['meta'] is not None:
                    cluster['description'] = ransom_data[0]['meta']
            if 'meta' not in cluster:
                cluster['meta'] = {}
            if 'links' not in cluster['meta']:
                cluster['meta']['links'] = []

            if 'locations' in ransom_data[0]:
                for location in ransom_data[0]['locations']:
                    if location['slug'] not in cluster['meta']['links']:
                        cluster['meta']['links'].append(location['slug'])

            if synonym:
                if 'synonyms' not in cluster['meta']:
                    cluster['meta']['synonyms'] = []
                    cluster['meta']['synonyms'].append(synonym)

            if 'refs' not in cluster['meta']:
                cluster['meta']['refs'] = []
            if 'profile' in ransom_data[0]:
                for url in ransom_data[0]['profile']:
                    if url not in cluster['meta']['refs']:
                        cluster['meta']['refs'].append(url)
            url = "https://www.ransomlook.io/group/" + true_rlookgroup
            if url not in cluster['meta']['refs']:
                cluster['meta']['refs'].append(url)

            if 'uuid' not in cluster:
                cluster['uuid'] = str(
                    uuid.uuid5(
                        uuid.UUID('10cf658b-5d32-4c4b-bb32-61760a640372'), rlookgroup
                    )
                )
            break

    if cluster_exist == True:
        updated.append(str(rlookgroup))
    else:
        # creating a new cluster
        created.append(str(rlookgroup))
        new_cluster = {}
        new_cluster['value'] = rlookgroup
        if ransom_data[0]['meta'] is not None:
            new_cluster['description'] = ransom_data[0]['meta']
        new_cluster['meta'] = {}

        new_cluster['meta']["links"] = []
        if 'locations' in ransom_data[0]:
            for location in ransom_data[0]['locations']:
                if location['slug'] not in new_cluster['meta']['links']:
                    new_cluster['meta']["links"].append(location['slug'])

        if synonym:
            new_cluster['meta']['synonyms'] = []
            new_cluster['meta']['synonyms'].append(synonym)

        new_cluster['meta']["refs"] = []

        url = "https://www.ransomlook.io/group/" + true_rlookgroup
        if url not in new_cluster['meta']['refs']:

            new_cluster['meta']['refs'].append(url)

        if 'profile' in ransom_data[0]:
            for url in ransom_data[0]['profile']:
                if url not in new_cluster['meta']['refs']:
                    new_cluster['meta']["refs"].append(url)
        new_cluster['uuid'] = str(
            uuid.uuid5(uuid.UUID('10cf658b-5d32-4c4b-bb32-61760a640372'), rlookgroup)
        )

        ransom_galaxy['values'].append(new_cluster)


print("\n" + str(len(updated)) + " clusters updated:")
print(updated)

print("\n" + str(len(created)) + " clusters created:")
print(created)

print("\nTotal modified :" + str(len(updated) + len(created)))

ransom_galaxy['version'] = ransom_galaxy['version'] + 1

tojson = json.dumps(ransom_galaxy, indent=2, ensure_ascii=False)
ransomware_galaxy = ransompath.open("w+")
ransomware_galaxy.write(tojson)
ransomware_galaxy.close()
