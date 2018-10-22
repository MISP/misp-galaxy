#!/usr/bin/env python3


import json
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Create a couple galaxy/cluster with cti\'s relationship\nMust be in the mitre/cti/enterprise-attack/relationship folder')
parser.add_argument("-p", "--path", required=True, help="Path of the mitre/cti folder")
args = parser.parse_args()



# read out all clusters and map them based on uuid


# build a mapping between uuids and Clusters
clusters = []
pathClusters = '../../../clusters'
for f in os.listdir(pathClusters):
    if '.json' in f:
        clusters.append(f)
clusters.sort()

cluster_uuids = {}
for cluster in clusters:
    fullPathClusters = os.path.join(pathClusters, cluster)
    with open(fullPathClusters) as fp:
        c = json.load(fp)
    for v in c['values']:
        if 'uuid' not in v:
            continue
        cluster_uuids[v['uuid']] = cluster


# read out all STIX mappings and store them in a list
stix_relations = {}
for subfolder in ['mobile-attack', 'pre-attack', 'enterprise-attack']:
    curr_dir = os.path.join(args.path, subfolder, 'relationship')
    for stix_fname in os.listdir(curr_dir):
        with open(os.path.join(curr_dir, stix_fname)) as f:
            json_data = json.load(f)
        for o in json_data['objects']:
            rel_type = o['relationship_type']
            dest_uuid = re.findall(r'--([0-9a-f-]+)', o['target_ref']).pop()
            uuid = re.findall(r'--([0-9a-f-]+)', o['source_ref']).pop()
            tags = []
            galaxy_fname = cluster_uuids[uuid]
            # print("{} \t {} \t {} \t {}".format(rel_type, uuid, dest_uuid, galaxy_fname))
            if not stix_relations.get(galaxy_fname):
                stix_relations[galaxy_fname] = {}
            stix_relations[galaxy_fname][uuid] = {
                "dest-uuid": dest_uuid,
                "tags": [
                    "estimative-language:likelihood-probability=\"almost-certain\""
                ],
                "type": rel_type
                }


# for each correlation per galaxy-file ,
#   open the file, 
#   add the relationship, 
#   and save the galaxy file 
for galaxy_fname, relations in stix_relations.items():
    print("############# {}".format(galaxy_fname))
    with open(os.path.join(pathClusters, galaxy_fname)) as f_in:
        file_json = json.load(f_in)

    for k, v in relations.items():
        # print("{} \t {}".format(k, v))
        for cluster in file_json['values']:
            if cluster['uuid'] == k:
                # skip if mapping already exists
                skip = False
                if 'related' in cluster:
                    for r in cluster['related']:
                        if r['dest-uuid'] == v['dest-uuid']:
                            print("  Mapping already exists! skipping... {}".format(v))
                            skip = True
                            break
                if skip:
                    break
                if 'related' not in cluster:
                    cluster['related'] = []
                cluster['related'].append(v)
                print("  Adding mapping: {}".format(v))
                break

    # increment version
    file_json['version'] += 1

    with open(os.path.join(pathClusters, galaxy_fname), 'w') as f_out:
        json.dump(file_json, f_out, indent=2, sort_keys=True, ensure_ascii=False)

    file_json = None
