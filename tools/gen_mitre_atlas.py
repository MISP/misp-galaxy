#!/usr/bin/env python3
import json
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Create a couple galaxy/cluster with MITRE ATLAS - Adversarial Threat Landscape for Artificial-Intelligence Systems\nMust be in the tools folder')
parser.add_argument("-p", "--path", required=True, help="Path of the mitre atlas-navigator-data folder")

args = parser.parse_args()

values = []
misp_dir = '../'


# domains = ['enterprise-attack', 'mobile-attack', 'pre-attack']
types = ['attack-pattern', 'course-of-action']
mitre_sources = ['mitre-atlas']

all_data = {}  # variable that will contain everything

# read in the non-MITRE data
# we need this to be able to build a list of non-MITRE-UUIDs which we will use later on
# to remove relations that are from MITRE.
# the reasoning is that the new MITRE export might contain less relationships than it did before
# so we cannot migrate all existing relationships as such
non_mitre_uuids = set()
for fname in os.listdir(os.path.join(misp_dir, 'clusters')):
    if 'mitre' in fname:
        continue
    if '.json' in fname:
        # print(fname)
        with open(os.path.join(misp_dir, 'clusters', fname)) as f_in:
            cluster_data = json.load(f_in)
            for cluster in cluster_data['values']:
                non_mitre_uuids.add(cluster['uuid'])

# read in existing MITRE data
# first build a data set of the MISP Galaxy ATT&CK elements by using the UUID as reference, this speeds up lookups later on.
# at the end we will convert everything again to separate datasets
all_data_uuid = {}

for t in types:
    fname = os.path.join(misp_dir, 'clusters', 'mitre-atlas-{}.json'.format(t))
    if os.path.exists(fname):
        # print("##### {}".format(fname))
        with open(fname) as f:
            file_data = json.load(f)
        # print(file_data)
        for value in file_data['values']:
            # remove (old)MITRE relations, and keep non-MITRE relations
            if 'related' in value:
                related_original = value['related']
                related_new = []
                for rel in related_original:
                    if rel['dest-uuid'] in non_mitre_uuids:
                        related_new.append(rel)
                value['related'] = related_new
            # find and handle duplicate uuids
            if value['uuid'] in all_data_uuid:
                # exit("ERROR: Something is really wrong, we seem to have duplicates.")
                # if it already exists we need to copy over all the data manually to merge it
                # on the other hand, from a manual analysis it looks like it's mostly the relations that are different
                # so now we will just copy over the relationships
                # actually, at time of writing the code below results in no change as the new items always contained more than the previously seen items
                value_orig = all_data_uuid[value['uuid']]
                if 'related' in value_orig:
                    for related_item in value_orig['related']:
                        if related_item not in value['related']:
                            value['related'].append(related_item)
            all_data_uuid[value['uuid']] = value

# now load the MITRE ATT&CK

attack_dir = os.path.join(args.path, 'dist')
if not os.path.exists(attack_dir):
    exit("ERROR: MITRE ATT&CK folder incorrect")

with open(os.path.join(attack_dir, 'stix-atlas.json')) as f:
    attack_data = json.load(f)

for item in attack_data['objects']:
    if item['type'] not in types:
        continue

    # print(json.dumps(item, indent=2, sort_keys=True, ensure_ascii=False))
    try:
        # build the new data structure
        value = {}
        uuid = re.search('--(.*)$', item['id']).group(0)[2:]
        # item exist already in the all_data set
        update = False
        if uuid in all_data_uuid:
            value = all_data_uuid[uuid]

        if 'description' in item:
            value['description'] = item['description']
        value['value'] = item['name']
        value['meta'] = {}
        value['meta']['refs'] = []
        value['uuid'] = re.search('--(.*)$', item['id']).group(0)[2:]

        for reference in item['external_references']:
            if 'url' in reference and reference['url'] not in value['meta']['refs']:
                value['meta']['refs'].append(reference['url'])
            # Find Mitre external IDs from allowed sources
            if 'external_id' in reference and reference.get("source_name", None) in mitre_sources:
                value['meta']['external_id'] = reference['external_id']
        if not value['meta'].get('external_id', None):
            # dataset also contains MITRE ATT&CK, whenever we don't find external ID from the allowed sources it's a sign that the entry is not of the type of interest
            continue
            # exit("Entry is missing an external ID, please update mitre_sources. Available references: {}".format(
            #     json.dumps(item['external_references'])
            # ))

        if 'kill_chain_phases' in item:   # many (but not all) attack-patterns have this
            value['meta']['kill_chain'] = []
            for killchain in item['kill_chain_phases']:
                value['meta']['kill_chain'].append(killchain['kill_chain_name'] + ':' + killchain['phase_name'])
        if 'x_mitre_data_sources' in item:
            value['meta']['mitre_data_sources'] = item['x_mitre_data_sources']
        if 'x_mitre_platforms' in item:
            value['meta']['mitre_platforms'] = item['x_mitre_platforms']
        # TODO add the other x_mitre elements dynamically

        # relationships will be build separately afterwards
        value['type'] = item['type']  # remove this before dump to json
        # print(json.dumps(value, sort_keys=True, indent=2))

        all_data_uuid[uuid] = value

    except Exception:
        print(json.dumps(item, sort_keys=True, indent=2))
        import traceback
        traceback.print_exc()

# process the 'relationship' type as we now know the existence of all ATT&CK uuids
for item in attack_data['objects']:
    if item['type'] != 'relationship':
        continue
    # print(json.dumps(item, indent=2, sort_keys=True, ensure_ascii=False))

    rel_type = item['relationship_type']
    dest_uuid = re.findall(r'--([0-9a-f-]+)', item['target_ref']).pop()
    source_uuid = re.findall(r'--([0-9a-f-]+)', item['source_ref']).pop()
    tags = []

    # add the relation in the defined way
    rel_source = {
        "dest-uuid": dest_uuid,
        "type": rel_type
    }
    if rel_type != 'subtechnique-of':
        rel_source['tags'] = [
            "estimative-language:likelihood-probability=\"almost-certain\""
        ]
    try:
        if 'related' not in all_data_uuid[source_uuid]:
            all_data_uuid[source_uuid]['related'] = []
        if rel_source not in all_data_uuid[source_uuid]['related']:
            all_data_uuid[source_uuid]['related'].append(rel_source)
    except KeyError:
        pass  # ignore relations from which we do not know the source

    # LATER find the opposite word of "rel_type" and build the relation in the opposite direction


# dump all_data to their respective file
for t in types:
    fname = os.path.join(misp_dir, 'clusters', 'mitre-atlas-{}.json'.format(t))
    if not os.path.exists(fname):
        exit("File {} does not exist, this is unexpected.".format(fname))
    with open(fname) as f:
        file_data = json.load(f)

    file_data['values'] = []
    for item in all_data_uuid.values():
        # print(json.dumps(item, sort_keys=True, indent=2))
        if 'type' not in item or item['type'] != t:  # drop old data or not from the right type
            continue
        item_2 = item.copy()
        item_2.pop('type', None)
        file_data['values'].append(item_2)

    # FIXME the sort algo needs to be further improved, potentially with a recursive deep sort
    file_data['values'] = sorted(file_data['values'], key=lambda x: x['meta']['external_id'])
    for item in file_data['values']:
        if 'related' in item:
            item['related'] = sorted(item['related'], key=lambda x: x['dest-uuid'])
        if 'meta' in item:
            if 'refs' in item['meta']:
                item['meta']['refs'] = sorted(item['meta']['refs'])
            if 'mitre_data_sources' in item['meta']:
                item['meta']['mitre_data_sources'] = sorted(item['meta']['mitre_data_sources'])
    file_data['version'] += 1
    with open(fname, 'w') as f:
        json.dump(file_data, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things

print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh.")
