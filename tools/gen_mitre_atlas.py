#!/usr/bin/env python3
"""Rebuild the MITRE ATLAS galaxies from the ATLAS knowledge base.

MITRE publishes ATLAS as a single YAML file, ``dist/ATLAS-latest.yaml`` in
https://github.com/mitre-atlas/atlas-data.  Everything else MITRE ships for ATLAS,
the STIX bundle of atlas-navigator-data this script used to read included, is
generated out of that file, so we read it directly: it is both ahead of the copies
and carries what the conversion into them drops -- the tactics, the sub-technique
tree, the case studies, the maturity, the platforms and the ATT&CK cross-references.

Every ATLAS object carries the UUID upstream assigns it, uuid5 of its ATLAS ID under
the ATLAS namespace, so our cluster UUIDs and any ATLAS-derived STIX agree, across
releases.

Usage:
    git clone https://github.com/mitre-atlas/atlas-data ../../atlas-data
    python3 gen_mitre_atlas.py -p ../../atlas-data
"""
import argparse
import json
import os
import re
import uuid

import yaml

misp_dir = '../'

# cluster name suffix -> the ATLAS export key holding those objects
types = {
    'attack-pattern': 'techniques',
    'course-of-action': 'mitigations',
    'case-study': 'case-studies',
}

# what a galaxy/cluster pair looks like the first time it is generated; the files are
# authoritative from then on, so that anything edited there by hand is not overwritten
new_files = {
    'case-study': {
        'name': 'MITRE ATLAS Case Studies',
        'description': 'Case studies from MITRE ATLAS (Adversarial Threat Landscape for '
                       'Artificial-Intelligence Systems), real-world incidents and red team '
                       'exercises against AI-enabled systems.',
        'category': 'incident',
        'icon': 'book',
        'cluster-uuid': '9f7e6548-4f70-459d-899e-580f282710ae',
        'galaxy-uuid': '2f6804b0-ac62-47bd-b847-5590dd9e0e94',
    },
}

# the route an object type lives under on atlas.mitre.org
routes = {
    'tactics': 'tactics',
    'techniques': 'techniques',
    'mitigations': 'mitigations',
    'case-studies': 'studies',
}

atlas_url = 'https://atlas.mitre.org'
kill_chain_name = 'mitre-atlas'
# uuid5 namespace ATLAS derives the UUID of an object from its ID with
atlas_namespace = uuid.UUID('atlas.mitre.org.'.encode('utf-8').hex())
almost_certain = ['estimative-language:likelihood-probability="almost-certain"']

# the ATT&CK galaxies an ``attack-reference`` can point into
attack_clusters = ['mitre-attack-pattern', 'mitre-course-of-action']

# descriptions cross-reference the rest of ATLAS relative to atlas.mitre.org, which
# leads nowhere once the description is read in MISP. The ID is matched loosely on
# purpose: upstream has typos in it (AMl.T0118.001), and a link is worth making
# absolute either way.
relative_link = re.compile(r'\]\(/({})/([^)\s]+)\)'.format('|'.join(sorted(set(routes.values())))))


def slug(name):
    """Tactic name to kill-chain phase, the way upstream atlas_to_stix.py builds it."""
    return name.lower().replace(' ', '-')


def absolute_links(description):
    """Make the ATLAS cross-references of a description resolvable from anywhere."""
    return relative_link.sub(
        lambda m: ']({}/{}/{})'.format(atlas_url, m.group(1), re.sub(r'^aml\.', 'AML.', m.group(2), flags=re.I)),
        description)


def load(path):
    with open(path) as f:
        return json.load(f)


def dump(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things


parser = argparse.ArgumentParser(
    description='Create the galaxies/clusters of MITRE ATLAS - Adversarial Threat Landscape '
                'for Artificial-Intelligence Systems\nMust be in the tools folder')
parser.add_argument('-p', '--path', required=True, help='Path of the mitre-atlas/atlas-data folder')
args = parser.parse_args()

atlas_file = os.path.join(args.path, 'dist', 'ATLAS-latest.yaml')
if not os.path.exists(atlas_file):
    exit('ERROR: {} not found, is --path pointing at the atlas-data folder?'.format(atlas_file))

with open(atlas_file) as f:
    export = yaml.safe_load(f)

print('Loading ATLAS {} (format {})'.format(export['collection']['version'], export['format-version']))

# ATLAS ID -> UUID, for every object a relation may have to point at
uuid_by_id = {}
for key in routes:
    for atlas_id, item in export[key].items():
        expected = str(uuid.uuid5(atlas_namespace, atlas_id))
        if item['uuid'] != expected:
            exit('ERROR: {} carries {}, expected {} - has the ATLAS UUID scheme changed?'.format(
                atlas_id, item['uuid'], expected))
        uuid_by_id[atlas_id] = item['uuid']

# ATT&CK ID -> UUID of the matching cluster value, to cross-link both frameworks
attack_uuid_by_id = {}
for cluster_name in attack_clusters:
    for value in load(os.path.join(misp_dir, 'clusters', cluster_name + '.json'))['values']:
        external_id = value.get('meta', {}).get('external_id')
        if external_id:
            attack_uuid_by_id.setdefault(external_id, value['uuid'])

# relations are stored per source object, grouped by type
achieves = {}     # technique -> the tactics it achieves, which is our kill chain
specializes = {}  # sub-technique -> its parent technique
mitigates = {}    # mitigation -> the techniques it mitigates
employs = {}      # case study -> the techniques it employs
sequences = []    # matrix -> its tactics, in matrix order
for source, groups in export['relationships'].items():
    for relation in groups.get('achieves', []):
        achieves.setdefault(source, []).append(relation['target'])
    for relation in groups.get('specializes', []):
        specializes[source] = relation['target']
    for relation in groups.get('mitigates', []):
        mitigates.setdefault(source, []).append(relation['target'])
    for relation in groups.get('employs', []):
        employs.setdefault(source, []).append(relation['target'])
    if source == export['matrix']['id']:
        sequences += groups.get('sequences', [])

# read in the non-MITRE data, so that relations other galaxies added to an ATLAS value
# survive the regeneration while the (possibly stale) MITRE ones are rebuilt
non_mitre_uuids = set()
for fname in os.listdir(os.path.join(misp_dir, 'clusters')):
    if 'mitre' in fname or not fname.endswith('.json'):
        continue
    for value in load(os.path.join(misp_dir, 'clusters', fname))['values']:
        non_mitre_uuids.add(value['uuid'])


def related(dest_id, rel_type, tagged=True):
    """Build a relation to an ATLAS object, or None when upstream does not know it."""
    if dest_id not in uuid_by_id:
        return None
    relation = {'dest-uuid': uuid_by_id[dest_id], 'type': rel_type}
    if tagged:
        relation['tags'] = list(almost_certain)
    return relation


def refs(item, key):
    urls = {'{}/{}/{}'.format(atlas_url, routes[key], item['id'])}
    for reference in item.get('references', []):
        if reference.get('url'):
            urls.add(reference['url'])
    if (item.get('attack-reference') or {}).get('url'):
        urls.add(item['attack-reference']['url'])
    return sorted(urls)


def build_value(atlas_id, item, key, kept_relations):
    value = {
        'description': absolute_links(item['description']),
        'meta': {
            'external_id': atlas_id,
            'refs': refs(item, key),
        },
        'uuid': item['uuid'],
        'value': '{} - {}'.format(item['name'], atlas_id),
    }
    meta = value['meta']
    relations = list(kept_relations.get(atlas_id, []))

    if key == 'techniques':
        meta['kill_chain'] = sorted(
            '{}:{}'.format(kill_chain_name, slug(export['tactics'][tactic]['name']))
            for tactic in achieves.get(atlas_id, []) if tactic in export['tactics'])
        meta['maturity'] = item['maturity']
        meta['mitre_platforms'] = item['platforms']
        if atlas_id in specializes:
            relations.append(related(specializes[atlas_id], 'subtechnique-of', tagged=False))
    elif key == 'mitigations':
        meta['categories'] = item['categories']
        meta['lifecycle_phases'] = item['lifecycle-phases']
        relations += [related(target, 'mitigates') for target in mitigates.get(atlas_id, [])]
    elif key == 'case-studies':
        meta['actor'] = item['actor']
        meta['case_study_type'] = item['type']
        meta['date'] = item['date']
        meta['date_granularity'] = item['date-granularity']
        meta['target'] = item['target']
        if item.get('reporter'):
            meta['reporter'] = item['reporter']
        relations += [related(target, 'uses') for target in employs.get(atlas_id, [])]

    # the ATT&CK entry this ATLAS entry derives from
    attack_id = (item.get('attack-reference') or {}).get('id')
    if attack_id:
        meta['mitre_attack_id'] = attack_id
        if attack_id in attack_uuid_by_id:
            relations.append({'dest-uuid': attack_uuid_by_id[attack_id],
                              'type': 'related-to', 'tags': list(almost_certain)})

    # a case study employs the same technique twice when it did so at two points of the
    # story, which is one relation to us
    deduplicated = []
    for relation in relations:
        if relation and relation not in deduplicated:
            deduplicated.append(relation)
    if deduplicated:
        value['related'] = sorted(deduplicated, key=lambda x: (x['dest-uuid'], x['type']))
    return value


def create_files(suffix):
    """Write the galaxy and the empty cluster of a type we did not carry before."""
    template = new_files.get(suffix)
    if not template:
        exit('clusters/mitre-atlas-{}.json does not exist, this is unexpected.'.format(suffix))
    galaxy = {
        'description': template['description'],
        'icon': template['icon'],
        'name': template['name'],
        'namespace': 'mitre',
        'type': 'mitre-atlas-{}'.format(suffix),
        'uuid': template['galaxy-uuid'],
        'version': 1,
    }
    dump(os.path.join(misp_dir, 'galaxies', 'mitre-atlas-{}.json'.format(suffix)), galaxy)
    return {
        'authors': ['MITRE'],
        'category': template['category'],
        'description': template['description'],
        'name': template['name'],
        'source': 'https://github.com/mitre-atlas/atlas-data',
        'type': 'mitre-atlas-{}'.format(suffix),
        'uuid': template['cluster-uuid'],
        'values': [],
        'version': 0,
    }


for suffix, key in sorted(types.items()):
    fname = os.path.join(misp_dir, 'clusters', 'mitre-atlas-{}.json'.format(suffix))
    file_data = load(fname) if os.path.exists(fname) else create_files(suffix)

    # keyed by ATLAS ID rather than by UUID, so that the relations other galaxies added
    # are kept even on a release that changes the UUID of a value
    kept_relations = {}
    for value in file_data['values']:
        external_id = value.get('meta', {}).get('external_id')
        kept = [relation for relation in value.get('related', [])
                if relation['dest-uuid'] in non_mitre_uuids]
        if external_id and kept:
            kept_relations[external_id] = kept

    file_data['values'] = sorted(
        (build_value(atlas_id, item, key, kept_relations) for atlas_id, item in export[key].items()),
        key=lambda x: x['meta']['external_id'])
    file_data['version'] += 1
    dump(fname, file_data)
    print('{}: {} values, {} relations'.format(
        os.path.basename(fname), len(file_data['values']),
        sum(len(value.get('related', [])) for value in file_data['values'])))

# the matrix orders the tactics, which is the kill chain order of the techniques galaxy
fname = os.path.join(misp_dir, 'galaxies', 'mitre-atlas-attack-pattern.json')
galaxy_data = load(fname)
kill_chain_order = [slug(export['tactics'][relation['target']]['name'])
                    for relation in sorted(sequences, key=lambda x: x['position'])
                    if relation['target'] in export['tactics']]
if galaxy_data.get('kill_chain_order', {}).get(kill_chain_name) != kill_chain_order:
    galaxy_data['kill_chain_order'] = {kill_chain_name: kill_chain_order}
    galaxy_data['version'] += 1
    dump(fname, galaxy_data)
    print('{}: kill chain order updated to the {} tactics of the matrix'.format(
        os.path.basename(fname), len(kill_chain_order)))

print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh.")
