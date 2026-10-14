#!/usr/bin/env python3
#
# MITRE ATLAS is published as a single YAML knowledge base:
#    https://github.com/mitre-atlas/atlas-data -> dist/ATLAS-latest.yaml
#
# Everything else MITRE ships for ATLAS (the website matrix, the Navigator
# layers, the STIX bundle, the Excel workbooks) is generated from that file.
# The STIX bundle carries neither the technique maturity, nor the mitigation
# categories and lifecycle phases, nor the case study type/actor/target/date,
# so we read the YAML directly.
import argparse
import json
import os
import re

import yaml

ATLAS_URL = 'https://atlas.mitre.org'

# object-type -> (cluster file suffix, atlas.mitre.org route)
OBJECT_TYPES = {
    'technique': ('attack-pattern', 'techniques'),
    'mitigation': ('course-of-action', 'mitigations'),
    'case-study': ('case-study', 'studies'),
}

# ATLAS entries carry an ATT&CK reference; resolve it against the galaxy that
# holds that kind of ATT&CK object.  Resolving on external_id alone is wrong:
# legacy ATT&CK mitigations reuse the ID of the technique they mitigate, so a
# technique reference such as T1596 also matches in mitre-course-of-action.
ATTACK_CLUSTER = {
    'technique': 'mitre-attack-pattern',
    'mitigation': 'mitre-course-of-action',
}

TAG_ALMOST_CERTAIN = 'estimative-language:likelihood-probability="almost-certain"'

parser = argparse.ArgumentParser(
    description='Create the MITRE ATLAS galaxies/clusters from the ATLAS knowledge base.\n'
                'Must be run from the tools folder.')
parser.add_argument('-p', '--path', required=True,
                    help='Path of the mitre-atlas/atlas-data folder')
parser.add_argument('-f', '--file', default=os.path.join('dist', 'ATLAS-latest.yaml'),
                    help='Knowledge base to read, relative to --path '
                         '(default: dist/ATLAS-latest.yaml)')
args = parser.parse_args()

misp_dir = '../'

atlas_file = os.path.join(args.path, args.file)
if not os.path.exists(atlas_file):
    exit('ERROR: {} not found. Point -p at a mitre-atlas/atlas-data checkout.'.format(atlas_file))

with open(atlas_file) as f:
    atlas = yaml.safe_load(f)

release = atlas['collection']['version']
print('Reading ATLAS {} from {}'.format(release, atlas_file))


def cluster_path(suffix):
    return os.path.join(misp_dir, 'clusters', 'mitre-atlas-{}.json'.format(suffix))


def absolute_links(text):
    """Rewrite atlas.mitre.org-relative cross-references into absolute URLs.

    ATLAS descriptions link as [Create Proxy AI Model](/techniques/AML.T0005),
    which resolves against atlas.mitre.org but leads nowhere inside MISP.
    """
    if not text:
        return text
    return re.sub(r'\]\((/(?:techniques|tactics|mitigations|studies)/)',
                  r'](' + ATLAS_URL + r'\1', text)


def refs_for(obj, route):
    refs = ['{}/{}/{}'.format(ATLAS_URL, route, obj['id'])]
    for reference in obj.get('references') or []:
        url = reference.get('url')
        if url and url not in refs:
            refs.append(url)
    return refs


# ---------------------------------------------------------------- lookups ---
# ATLAS ID -> uuid, for every object type.  These uuids are uuid5 values
# assigned by ATLAS itself and are stable across releases, so relations can be
# rebuilt from the knowledge base on every run.
uuid_by_id = {}
for section in ('tactics', 'techniques', 'mitigations', 'case-studies'):
    for atlas_id, obj in atlas[section].items():
        uuid_by_id[atlas_id] = obj['uuid']

tactic_slug = {}
for atlas_id, tactic in atlas['tactics'].items():
    tactic_slug[atlas_id] = tactic['name'].lower().replace(' ', '-').replace('&', 'and')

relationships = atlas['relationships']

# ATT&CK external_id -> uuid, per galaxy that can be the target of a reference
attack_uuid = {}
for object_type, cluster_name in ATTACK_CLUSTER.items():
    attack_uuid[object_type] = {}
    with open(os.path.join(misp_dir, 'clusters', '{}.json'.format(cluster_name))) as f:
        for value in json.load(f)['values']:
            external_id = value.get('meta', {}).get('external_id')
            if external_id:
                attack_uuid[object_type].setdefault(external_id, value['uuid'])

# ------------------------------------------------- existing galaxy content ---
# Keep relations that were curated by hand in MISP: anything pointing at a
# non-MITRE cluster.  Everything MITRE-sourced is rebuilt from the ATLAS data
# below, since a new release may well contain fewer relations than the last.
non_mitre_uuids = set()
for fname in os.listdir(os.path.join(misp_dir, 'clusters')):
    if 'mitre' in fname or not fname.endswith('.json'):
        continue
    with open(os.path.join(misp_dir, 'clusters', fname)) as f:
        for value in json.load(f)['values']:
            non_mitre_uuids.add(value['uuid'])

# ATLAS ID -> the uuid the value carries today, so incoming relations in other
# clusters can be remapped onto the upstream uuid without losing anything.
old_uuid_by_id = {}
kept_relations = {}
for object_type, (suffix, _route) in OBJECT_TYPES.items():
    fname = cluster_path(suffix)
    if not os.path.exists(fname):
        continue
    with open(fname) as f:
        for value in json.load(f)['values']:
            external_id = value.get('meta', {}).get('external_id')
            if not external_id:
                continue
            old_uuid_by_id[external_id] = value['uuid']
            kept = [rel for rel in value.get('related', [])
                    if rel['dest-uuid'] in non_mitre_uuids]
            if kept:
                kept_relations[external_id] = kept

# ------------------------------------------------------------ build values ---
values_by_type = {object_type: [] for object_type in OBJECT_TYPES}

for section, object_type in (('techniques', 'technique'),
                             ('mitigations', 'mitigation'),
                             ('case-studies', 'case-study')):
    route = OBJECT_TYPES[object_type][1]
    for atlas_id, obj in sorted(atlas[section].items()):
        meta = {
            'external_id': atlas_id,
            'refs': refs_for(obj, route),
        }
        value = {
            'description': absolute_links(obj.get('description', '')),
            'meta': meta,
            'uuid': obj['uuid'],
            # ATLAS values are named "<name> - <ATLAS ID>", the convention the
            # other MITRE galaxies follow.
            'value': '{} - {}'.format(obj['name'], atlas_id),
        }

        if object_type == 'technique':
            meta['kill_chain'] = sorted(
                'mitre-atlas:{}'.format(tactic_slug[rel['target']])
                for rel in relationships.get(atlas_id, {}).get('achieves', []))
            meta['mitre_platforms'] = obj['platforms']
            meta['maturity'] = obj['maturity']
        elif object_type == 'mitigation':
            meta['categories'] = obj['categories']
            meta['lifecycle_phases'] = obj['lifecycle-phases']
        elif object_type == 'case-study':
            meta['case_study_type'] = obj['type']
            meta['actor'] = obj['actor']
            meta['target'] = obj['target']
            meta['date'] = obj['date']
            meta['date_granularity'] = obj['date-granularity']

        attack_reference = obj.get('attack-reference')
        if attack_reference:
            meta['mitre_attack_id'] = attack_reference['id']

        related = list(kept_relations.get(atlas_id, []))

        def add(dest_uuid, rel_type, tagged=True):
            rel = {'dest-uuid': dest_uuid, 'type': rel_type}
            if tagged:
                rel['tags'] = [TAG_ALMOST_CERTAIN]
            if rel not in related:
                related.append(rel)

        rels = relationships.get(atlas_id, {})
        for rel in rels.get('specializes', []):
            add(uuid_by_id[rel['target']], 'subtechnique-of', tagged=False)
        for rel in rels.get('mitigates', []):
            add(uuid_by_id[rel['target']], 'mitigates')
        # A case study employs a technique once per step, so the same pair can
        # appear several times; add() keeps one relation per pair.
        for rel in rels.get('employs', []):
            add(uuid_by_id[rel['target']], 'uses')

        if attack_reference and object_type in ATTACK_CLUSTER:
            dest = attack_uuid[object_type].get(attack_reference['id'])
            if dest:
                add(dest, 'related-to')
            else:
                print('  WARNING: {} references ATT&CK {}, not found in {}'.format(
                    atlas_id, attack_reference['id'], ATTACK_CLUSTER[object_type]))

        if related:
            value['related'] = sorted(related, key=lambda x: (x['type'], x['dest-uuid']))

        values_by_type[object_type].append(value)

# ------------------------------------------------------------------ output ---
for object_type, (suffix, _route) in OBJECT_TYPES.items():
    fname = cluster_path(suffix)
    if not os.path.exists(fname):
        print('SKIPPED {}: file does not exist yet.'.format(fname))
        continue
    with open(fname) as f:
        file_data = json.load(f)
    file_data['source'] = 'https://github.com/mitre-atlas/atlas-data'
    file_data['values'] = sorted(values_by_type[object_type],
                                 key=lambda x: x['meta']['external_id'])
    file_data['version'] += 1
    with open(fname, 'w') as f:
        json.dump(file_data, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write('\n')
    print('{}: {} values'.format(fname, len(file_data['values'])))

# The kill chain order comes from the matrix itself rather than being kept by
# hand, so a reordered or extended matrix follows automatically.
galaxy_file = os.path.join(misp_dir, 'galaxies', 'mitre-atlas-attack-pattern.json')
with open(galaxy_file) as f:
    galaxy_data = json.load(f)
sequences = sorted(relationships[atlas['matrix']['id']]['sequences'],
                   key=lambda x: x['position'])
galaxy_data['kill_chain_order'] = {
    'mitre-atlas': [tactic_slug[rel['target']] for rel in sequences]
}
galaxy_data['version'] += 1
with open(galaxy_file, 'w') as f:
    json.dump(galaxy_data, f, indent=2, sort_keys=True, ensure_ascii=False)
    f.write('\n')
print('{}: {} tactics'.format(galaxy_file, len(sequences)))

# ------------------------------------------- remap relations in other clusters ---
# The uuids above are ATLAS's own; where a value used to carry a different one,
# every relation pointing at it has to follow.  Relations to entries ATLAS has
# retired are dropped.
remap = {old_uuid: uuid_by_id[atlas_id]
         for atlas_id, old_uuid in old_uuid_by_id.items()
         if atlas_id in uuid_by_id and uuid_by_id[atlas_id] != old_uuid}
retired = {old_uuid for atlas_id, old_uuid in old_uuid_by_id.items()
           if atlas_id not in uuid_by_id}
if retired:
    print('Retired upstream: {}'.format(sorted(
        atlas_id for atlas_id in old_uuid_by_id if atlas_id not in uuid_by_id)))

atlas_files = {os.path.basename(cluster_path(suffix)) for suffix, _ in OBJECT_TYPES.values()}
for fname in sorted(os.listdir(os.path.join(misp_dir, 'clusters'))):
    if not fname.endswith('.json') or fname in atlas_files:
        continue
    path = os.path.join(misp_dir, 'clusters', fname)
    with open(path) as f:
        file_data = json.load(f)
    changed = 0
    dropped = 0
    for value in file_data['values']:
        if 'related' not in value:
            continue
        kept = []
        for rel in value['related']:
            if rel['dest-uuid'] in retired:
                dropped += 1
                continue
            if rel['dest-uuid'] in remap:
                rel['dest-uuid'] = remap[rel['dest-uuid']]
                changed += 1
            kept.append(rel)
        value['related'] = kept
    if changed or dropped:
        file_data['version'] += 1
        with open(path, 'w') as f:
            json.dump(file_data, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write('\n')
        print('{}: {} relations remapped, {} dropped'.format(fname, changed, dropped))

print("All done, please don't forget to ./jq_all_the_things.sh, commit, "
      "and then ./validate_all.sh, and also update_README_with_index.py.")
