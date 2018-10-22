#!/usr/bin/env python3
# TODO
# - define strength between relations based on 'type' - similar should be closer than the others
# - use different colors / shapes

import json
import os
import argparse
from graphviz import Digraph


parser = argparse.ArgumentParser(description='Generate a DOT file to graph a Galaxy cluster and its relations.')
parser.add_argument("-u", "--uuid", help="Start UUID of a cluster.")
parser.add_argument("-a", "--all", action='store_true', help='generate all graphs as PNGs')
args = parser.parse_args()


def gen_galaxy_tag(galaxy_name, cluster_name):
    # return 'misp-galaxy:{}="{}"'.format(galaxy_name, cluster_name)
    return '{}={}'.format(galaxy_name, cluster_name)

files_to_ignore = ['mitre-attack-pattern.json', 'mitre-course-of-action.json', 'mitre-intrusion-set.json',
                   'mitre-malware.json', 'mitre-tool.json']

galaxies_fnames = []
pathClusters = '../clusters'
for f in os.listdir(pathClusters):
    if '.json' in f and f not in files_to_ignore:
        galaxies_fnames.append(f)
galaxies_fnames.sort()

cluster_uuids = {}
galaxies = []
for galaxy_fname in galaxies_fnames:
    fullPathClusters = os.path.join(pathClusters, galaxy_fname)
    with open(fullPathClusters) as fp:
        json_data = json.load(fp)
    galaxies.append(json_data)
    for cluster in json_data['values']:
        if 'uuid' not in cluster:
            continue
        cluster_uuids[cluster['uuid']] = {
            'tag': gen_galaxy_tag(json_data['type'], cluster['value']),
            'galaxy': json_data['type'],
            'value': cluster['value'],
            'synonyms': cluster.get('synonyms')
        }



# for k, v in cluster_uuids.items():
#     print("{}\t{}".format(k, v))


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


def gen_dot(uuid):
    things_to_keep = [uuid]  # '5b4ee3ea-eee3-4c8e-8323-85ae32658754' = threat-actor=Sofacy
                             # ' 5e0a7cf2-6107-4d5f-9dd0-9df38b1fcba8' = APT30
    things_seen = things_to_keep.copy()

    dot = []
    while len(things_to_keep) > 0:
        new_things_to_keep = []
        for galaxy in galaxies:
            for cluster in galaxy['values']:
                if 'related' not in cluster:
                    continue
                src_tag = gen_galaxy_tag(galaxy['type'], cluster['value'])
                if cluster['uuid'] not in things_to_keep:
                    continue
                node_params = []
                node_params.append('label="{}&#92;n{}"'.format(galaxy['type'], cluster['value']))
                if type_mapping.get(galaxy['type']) == 'actor':
                    node_params.append('shape=octagon')
                    node_params.append('style=filled,color=indianred1')
                elif type_mapping.get(galaxy['type']) == 'tool':
                    node_params.append('shape=box')
                    node_params.append('style=filled,color=deepskyblue')
                else:
                    node_params.append('shape=ellipse')
                dot.append('"{src}" [{params}];'.format(
                            src=src_tag,
                            params=','.join(node_params)
                        ))
                for relation in cluster['related']:
                    try:
                        dest_tag = cluster_uuids[relation['dest-uuid']]['tag']
                        extra = []
                        if relation['type'] == 'similar':
                            # make arrow bidirectional
                            extra.append('dir="both"')
                            # prevent double links for 'similar' types
                            if relation['dest-uuid'] in things_seen:
                                continue
                        dot.append('"{src}" -> "{dst}" [label="{lbl}",{extra}];'.format(
                        # dot.append('"{src}" -> "{dst}" [{extra}];'.format(
                            src=src_tag,
                            dst=dest_tag,
                            lbl=relation['type'],
                            extra=','.join(extra)
                        ))
                        # FIXME - add a separate node with the color, type, format of the source-node

                        # prevent something to be processed twice
                        if relation['dest-uuid'] not in things_seen:
                            new_things_to_keep.append(relation['dest-uuid'])
                        things_seen.append(relation['dest-uuid'])
                    except KeyError:
                        # skip uuids not found
                        pass
        # print(new_things_to_keep)
        things_to_keep = new_things_to_keep.copy()


    return dot

if args.uuid:
    uuid = args.uuid
    dot = []
    # dot.append('digraph G {')
    dot.append('concentrate=true;')
    dot.append('overlap=scale;')
    generated_dot = gen_dot(uuid)
    if len(generated_dot) == 0:
        print("Empty graph for uuid: {}".format(uuid))
        exit()
    print("Generating graph for uuid: {}".format(uuid))
    dot += generated_dot
    # dot.append('}')
    # dg.source = '\n'.join(dot)
    dg = Digraph(engine='neato', format='png', body=dot)
    # print(dg.source)
    dg.render(filename='graphs/{}'.format(uuid), cleanup=False)

elif args.all:
    for uuid in cluster_uuids.keys():
        dot = []
        # dot.append('digraph G {')
        dot.append('concentrate=true;')
        dot.append('overlap=scale;')
        generated_dot = gen_dot(uuid)
        if len(generated_dot) == 0:
            print("Empty      graph for uuid: {}".format(uuid))
            continue

        print("Generating graph for uuid: {}".format(uuid))
        dot += generated_dot
        # dot.append('}')
        # dg.source = '\n'.join(dot)

        dg = Digraph(format='png', body=dot)
        #print(dg.source)
        dg.render(filename='graphs/{}'.format(uuid))
else:
    exit("No parameters given, use --help for more info.")
