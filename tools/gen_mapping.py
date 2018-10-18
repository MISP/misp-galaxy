#!/usr/bin/env python3
'''
Author: Christophe Vandeplas
License: AGPL v3

This builds an automatic mapping between the galaxy clusters of the same type.
The mapping is made by using the synonyms documented in each cluster.

The output is saved in the cluster files themselves, if a change is done the version number is increased.
(commented out) The output is saved in a file called "mapping_XXX.json".

# TODO add a blacklist support for blacklisted mappings
'''
import json
import os


# Some galaxy clusters have overlapping synonyms, while not being of the same type.
# This type_mapping is there to distinguish galaxies based on their type.
# Example: A galaxy of type 'actor' should not map to a galaxy of type 'tool', even if the name/synonym is the same.
type_mapping = {
    'ransomware': 'tool',
    # 'mitre-pre-attack-relationship': '',
    # 'mitre-enterprise-attack-course-of-action': '',
    'mitre-enterprise-attack-intrusion-set': 'actor',
    'mitre-intrusion-set': 'actor',
    'rat': 'tool',
    'stealer': 'tool',
    'mitre-enterprise-attack-malware': 'tool',
    # 'mitre-attack-pattern': '',
    # 'mitre-mobile-attack-relationship': '',
    # 'mitre-enterprise-attack-attack-pattern': '',
    'microsoft-activity-group': 'actor',
    # 'mitre-course-of-action': '',
    'exploit-kit': 'tool',
    'mitre-mobile-attack-tool': 'tool',
    'backdoor': 'tool',
    # 'mitre-pre-attack-attack-pattern': '',
    'mitre-mobile-attack-intrusion-set': 'actor',
    'mitre-tool': 'tool',
    # 'mitre-mobile-attack-attack-pattern': '',
    'mitre-mobile-attack-malware': 'tool',
    'tool': 'tool',
    # 'preventive-measure': '',
    # 'sector': '',
    'mitre-malware': 'tool',
    'banker': 'tool',
    # 'branded-vulnerability': '',
    'botnet': 'tool',
    # 'cert-eu-govsector': '',
    'threat-actor': 'actor',
    'mitre-enterprise-attack-tool': 'tool',
    'android': 'tool',
    # 'mitre-mobile-attack-course-of-action': '',
    'mitre-pre-attack-intrusion-set': 'actor',
    # 'mitre-enterprise-attack-relationship': '',
    'tds': 'tool',
    'malpedia': 'tool'
}


def loadjsons(path):
    """
      Find all Jsons and load them in a dict
    """
    files = []
    data = []
    for name in os.listdir(path):
        if os.path.isfile(os.path.join(path, name)) and name.endswith('.json'):
            files.append(name)
    for jfile in files:
        data.append(json.load(open("%s/%s" % (path, jfile))))
    return data


def printjson(s):
    print(json.dumps(s, sort_keys=True, indent=4, separators=(',', ': ')))


def to_tag(t, v):
    return 'misp-galaxy:{}="{}"'.format(t, v)


def get_cluster_uuid(cluster):
    uuid = cluster.get('uuid')
    if not uuid:  # FIXME are these bugs in the format? - mitre-tool.json
        uuid = cluster['meta'].get('uuid')
    if not uuid:
        print(cluster)
        exit("ERROR: missing UUID in cluster")
    return uuid


if __name__ == '__main__':
    path = '../clusters'
    jsons = loadjsons(path)
    mappings = {}
    for k, v in type_mapping.items():
        if v not in mappings:
            mappings[v] = []

    for djson in jsons:
        galaxy = djson['type']

        # ignore the galaxies that are not relevant for us
        if galaxy not in type_mapping:
            print("Ignoring galaxy '{}' as it is not in the mapping.".format(galaxy))
            continue

        # process the entries in each cluster
        clusters = djson.get('values')
        for cluster in clusters:
            names = [cluster['value']]

            if 'meta' in cluster and 'synonyms' in cluster['meta']:
                names += [s for s in cluster['meta']['synonyms']]

            # check if the entry is already in our mappings dict
            seen_once = False
            for mapping in mappings[type_mapping[galaxy]]:
                seen = False
                # name is known, add the synonyms and tags
                for name in names:
                    if name in mapping['names']:
                        seen = True
                        seen_once = True
                # we have a match in this mapping, add name and synonyms
                if seen:
                    for name in names:
                        if name not in mapping['names']:
                            mapping['names'].append(name)
                    tag = to_tag(galaxy, cluster['value'])
                    if tag not in mapping['values']:
                        mapping['values'].append(tag)
                    uuid = get_cluster_uuid(cluster)
                    if uuid not in mapping['uuids']:
                        mapping['uuids'].append(uuid)

            # it's not in any mapping, add it
            if not seen_once:
                mapping = {}
                mapping['names'] = names
                mapping['values'] = [to_tag(galaxy, cluster['value'])]
                uuid = get_cluster_uuid(cluster)
                mapping['uuids'] = [uuid]
                mappings[type_mapping[galaxy]].append(mapping)

    # We have our nice mapping.
    # Now we only need to add it again in the original files.
    for name in os.listdir(path):
        # skip files that are not relevant
        if not (os.path.isfile(os.path.join(path, name)) and name.endswith('.json')):
            continue

        # load json
        with open(os.path.join(path, name), 'r') as f_in:
            file_json = json.load(f_in)
        galaxy = file_json['type']

        # ignore the galaxies that are not relevant for us
        if galaxy not in type_mapping:
            continue

        changed = False
        for cluster in file_json['values']:
            for mapping in mappings[type_mapping[galaxy]]:
                cluster_uuid = get_cluster_uuid(cluster)
                if cluster_uuid not in mapping['uuids']:
                    continue
                # uuid is in the mappings
                for uuid in mapping['uuids']:
                    # skip self
                    if uuid == cluster_uuid:
                        continue
                    # skip existing entries
                    if 'related' in cluster:
                        if any(v['dest-uuid'] == uuid for v in cluster['related']):
                            continue
                    # initialize array
                    if 'related' not in cluster:
                        cluster['related'] = []
                    # automated things are set to likely
                    # manual validation can upgrade to very-likely or almost-certain
                    cluster['related'].append({"dest-uuid": uuid,
                                               "type": "similar",
                                               "tags": [
                                                   "estimative-language:likelihood-probability=\"likely\""
                                               ]
                                               })
                    changed = True
        if changed:
            file_json['version'] += 1

            # save result to the original file
            with open(os.path.join(path, name), 'w') as f_out:
                json.dump(file_json, f_out, indent=2, sort_keys=True, ensure_ascii=False)

            print("Updated file {}".format(name))
    print("All done, please don't forget to ./validate_all.sh and ./jq_all_the_things.sh")

    # # simply dump the mapping_json to files. This is not really needed anymore
    # for galaxy_type, vals in mappings.items():
    #     for mapping in vals:
    #         mapping['names'].sort()
    #         mapping['values'].sort()
    #     with open('mapping_{}.json'.format(galaxy_type), 'w') as f:
    #         json.dump(vals, f, sort_keys=True, indent=4, separators=(',', ': '))
    #     print("File saved as mapping_{}.json".format(galaxy_type))
