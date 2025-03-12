#!/usr/bin/env python3
import json
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Create a couple galaxy/cluster with cti\'s intrusion-sets\nMust be in the tools folder')
parser.add_argument("-p", "--path", required=True, help="Path of the mitre/cti folder")

args = parser.parse_args()
root_folder = args.path

values = []
misp_dir = '../'


domains = ['enterprise-attack', 'mobile-attack', 'pre-attack']
types = {'data-source': 'x-mitre-data-source',
         'attack-pattern': 'attack-pattern',
         'course-of-action': 'course-of-action',
         'intrusion-set': 'intrusion-set',
         'malware': 'malware',
         'tool': 'tool',
         'data-component': 'x-mitre-data-component'
         }
mitre_sources = ['mitre-attack', 'mitre-ics-attack', 'mitre-pre-attack', 'mitre-mobile-attack']


kill_chain_order_sort_order = {
    "attack": [
        "reconnaissance",
        "resource-development",
        "initial-access",
        "execution",
        "persistence",
        "privilege-escalation",
        "defense-evasion",
        "credential-access",
        "discovery",
        "lateral-movement",
        "collection",
        "command-and-control",
        "exfiltration",
        "impact"
    ],
    "mobile-attack": [
        "initial-access",
        "execution",
        "persistence",
        "privilege-escalation",
        "defense-evasion",
        "credential-access",
        "discovery",
        "lateral-movement",
        "collection",
        "command-and-control",
        "exfiltration",
        "impact",
        "network-effects",
        "remote-service-effects"
    ],
    "pre-attack": [
        "priority-definition-planning",
        "priority-definition-direction",
        "target-selection",
        "technical-information-gathering",
        "people-information-gathering",
        "organizational-information-gathering",
        "technical-weakness-identification",
        "people-weakness-identification",
        "organizational-weakness-identification",
        "adversary-opsec",
        "establish-&-maintain-infrastructure",
        "persona-development",
        "build-capabilities",
        "test-capabilities",
        "stage-capabilities",
        "launch",     # added manually
        "compromise"  # added manually
    ]
}


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
    fname = os.path.join(misp_dir, 'clusters', 'mitre-{}.json'.format(t))
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
for domain in domains:
    attack_dir = os.path.join(root_folder, domain)
    if not os.path.exists(attack_dir):
        exit("ERROR: MITRE ATT&CK folder incorrect")

    with open(os.path.join(attack_dir, domain + '.json')) as f:
        attack_data = json.load(f)

    for item in attack_data['objects']:
        if item['type'] not in types.values():
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
            if 'external_references' in item:
                value['value'] = item['name'] + ' - ' + item['external_references'][0]['external_id']
            else:
                value['value'] = item['name']
            value['meta'] = {}
            value['meta']['refs'] = []
            value['uuid'] = re.search('--(.*)$', item['id']).group(0)[2:]

            if 'aliases' in item:
                value['meta']['synonyms'] = item['aliases']
            if 'x_mitre_aliases' in item:
                value['meta']['synonyms'] = item['x_mitre_aliases']

            # handle deprecated and/or revoked
            # if 'x_mitre_deprecated' in item and item['x_mitre_deprecated']:
            #     value['deprecated'] = True
            if 'revoked' in item and item['revoked']:
                value['revoked'] = True

            if 'external_references' in item:
                for reference in item['external_references']:
                    if 'url' in reference and reference['url'] not in value['meta']['refs']:
                        value['meta']['refs'].append(reference['url'])
                    # Find Mitre external IDs from allowed sources
                    if 'external_id' in reference and reference.get("source_name", None) in mitre_sources:
                        value['meta']['external_id'] = reference['external_id']
                if not value['meta'].get('external_id', None):
                    exit("Entry is missing an external ID, please update mitre_sources. Available references: {}".format(
                        json.dumps(item['external_references'])
                    ))

            if 'kill_chain_phases' in item:   # many (but not all) attack-patterns have this
                value['meta']['kill_chain'] = []
                for killchain in item['kill_chain_phases']:
                    kill_chain_name = killchain['kill_chain_name'][6:]
                    phase_name = killchain['phase_name']
                    if 'x_mitre_platforms' in item:
                        for platform in item['x_mitre_platforms']:
                            platform = platform.replace(' ', '-')
                            value['meta']['kill_chain'].append(f"{kill_chain_name}-{platform}:{phase_name}")
                    else:
                        value['meta']['kill_chain'].append(f"{kill_chain_name}:{phase_name}")
            if 'x_mitre_data_sources' in item:
                value['meta']['mitre_data_sources'] = item['x_mitre_data_sources']
            if 'x_mitre_platforms' in item:
                value['meta']['mitre_platforms'] = item['x_mitre_platforms']
            # TODO add the other x_mitre elements dynamically, but now it seems to break the tests
            # x_mitre_fields = [key for key in item.keys() if key.startswith('x_mitre')]
            # skip_x_mitre_fields = ['x_mitre_deprecated', 'x_mitre_aliases', 'x_mitre_version', 'x_mitre_old_attack_id', 'x_mitre_attack_spec_version']
            # for skip_field in skip_x_mitre_fields:
            #     try:
            #         x_mitre_fields.remove(skip_field)
            #     except ValueError:
            #         pass
            # for x_mitre_field in x_mitre_fields:
            #     value['meta'][x_mitre_field[2:]] = item[x_mitre_field]

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
        try:
            if 'related' not in all_data_uuid[source_uuid]:
                all_data_uuid[source_uuid]['related'] = []
            if rel_source not in all_data_uuid[source_uuid]['related']:
                all_data_uuid[source_uuid]['related'].append(rel_source)
        except KeyError:
            pass  # ignore relations from which we do not know the source

        # LATER find the opposite word of "rel_type" and build the relation in the opposite direction

    # process (again) the data-component, as they create relationships using 'x_mitre_data_source_ref' instead...
    for item in attack_data['objects']:
        if item['type'] != 'x-mitre-data-component':
            continue
        data_source_uuid = re.findall(r'--([0-9a-f-]+)', item['x_mitre_data_source_ref']).pop()
        data_component_uuid = re.findall(r'--([0-9a-f-]+)', item['id']).pop()
        # create relationship bidirectionally
        rel_data_source = {
            "dest-uuid": data_component_uuid,
            "type": 'includes'  # FIXME use a valid type
        }
        try:
            if 'related' not in all_data_uuid[data_source_uuid]:
                all_data_uuid[data_source_uuid]['related'] = []
            if rel_data_source not in all_data_uuid[data_source_uuid]['related']:
                all_data_uuid[data_source_uuid]['related'].append(rel_data_source)
        except KeyError:
            pass  # ignore relations from which we do not know the source
        rel_data_component = {
            "dest-uuid": data_component_uuid,
            "type": 'included-in'  # FIXME use a valid type
        }
        try:
            if 'related' not in all_data_uuid[data_component_uuid]:
                all_data_uuid[data_component_uuid]['related'] = []
            if rel_data_component not in all_data_uuid[data_component_uuid]['related']:
                all_data_uuid[data_component_uuid]['related'].append(rel_data_component)
        except KeyError:
            pass  # ignore relations from which we do not know the source


# dump all_data to their respective file
for t, meta_t in types.items():
    kill_chain_order = {}

    fname = os.path.join(misp_dir, 'clusters', 'mitre-{}.json'.format(t))
    if not os.path.exists(fname):
        exit("File {} does not exist, this is unexpected.".format(fname))
    with open(fname) as f:
        file_data = json.load(f)

    file_data['values'] = []
    for item in all_data_uuid.values():
        # print(json.dumps(item, sort_keys=True, indent=2))
        if 'type' not in item or item['type'] != meta_t:  # drop old data or not from the right type
            continue
        item_2 = item.copy()
        item_2.pop('type', None)
        file_data['values'].append(item_2)
        for kill_chains in item['meta'].get('kill_chain', []):
            kill_chain_name, kill_chain_phase = kill_chains.split(':')
            if kill_chain_name not in kill_chain_order:
                kill_chain_order[kill_chain_name] = set()
            kill_chain_order[kill_chain_name].add(kill_chain_phase)

    # FIXME the sort algo needs to be further improved, potentially with a recursive deep sort
    file_data['values'] = sorted(file_data['values'], key=lambda x: sorted(x['value']))
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

    # rebuild the galaxies file with kill_chains
    # OK, this is really inefficient, but just the easiest way to get it done now
    fname_galaxy = os.path.join(misp_dir, 'galaxies', 'mitre-{}.json'.format(t))
    if not os.path.exists(fname_galaxy):
        exit("File {} does not exist, this is unexpected.".format(fname_galaxy))
    with open(fname_galaxy) as f_galaxy:
        file_data_galaxy = json.load(f_galaxy)

    # sort the kill chain order in the right way, using the kill_chain_order_sort_order
    kill_chain_order_sorted = {}
    for kill_chain_name, kill_chain_phases in kill_chain_order.items():
        for kill_chain_order_sort_order_key in kill_chain_order_sort_order.keys():
            if kill_chain_name.startswith(kill_chain_order_sort_order_key):
                try:
                    kill_chain_order_sorted[kill_chain_name] = sorted(
                        list(kill_chain_phases),
                        key=kill_chain_order_sort_order[kill_chain_order_sort_order_key].index)
                except ValueError as e:
                    print("ERROR:")
                    print(f"- Kill chain: {kill_chain_name}")
                    print(f"- Kill chain phases: {kill_chain_phases}")
                    print(f"- Kill chain order sort order: {kill_chain_order_sort_order[kill_chain_order_sort_order_key]}")
                    exit(f"ERROR: kill_chain_order_sort_order does not contain a key for {kill_chain_name} - {e}. Please add it manually in the code.")

    if kill_chain_order_sorted:
        file_data_galaxy['kill_chain_order'] = dict(sorted(kill_chain_order_sorted.items()))
        file_data_galaxy['version'] += 1
    with open(fname_galaxy, 'w') as f_galaxy:
        json.dump(file_data_galaxy, f_galaxy, indent=2, sort_keys=True, ensure_ascii=False)
        f_galaxy.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things


print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh.")
