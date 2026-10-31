#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    A simple convertor of the MITRE D3FEND to a MISP Galaxy datastructure.
#    Copyright (C) 2024 Christophe Vandeplas
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import json
import os
import uuid
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import requests

# The bulk mappings dump (api/ontology/inference/d3fend-full-mappings.json) was
# removed from the site in the D3FEND 1.6.0 release. The per-technique API
# returns the same query results, one technique at a time.
API_URL = 'https://d3fend.mitre.org/api'
TECHNIQUE_URL = 'https://d3fend.mitre.org/technique'

galaxy_fname = 'mitre-d3fend.json'
galaxy_type = "mitre-d3fend"
galaxy_name = "MITRE D3FEND Techniques"
galaxy_description = 'Defensive countermeasure techniques from MITRE D3FEND.'
galaxy_source = 'https://d3fend.mitre.org/'

uuid_seed = '35527064-12b4-4b73-952b-6d76b9f1b1e3'

# D3FEND has no uuids of its own: a technique is identified by its IRI and by
# d3f:d3fend-id, and since 1.3.0 both are derived from the label. Renaming a
# technique therefore moves its id and, with it, the uuid we mint from that id -
# D3-FR "File Removal" became D3-FEV "File Eviction" in 1.6.0. Upstream records
# none of this: the old class is deleted from the ontology outright, and
# owl:deprecated is only ever set on the offensive (ATT&CK/SPARTA) classes, so a
# rename is indistinguishable from a removal except through the mappings the old
# and the new id share.
successor_link_ratio = 0.8   # link the revoked technique to its successor
successor_hint_ratio = 0.5   # only report the candidate, the call is a human one

misp_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
default_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cache', 'd3fend')

# offensive framework -> cluster holding the techniques of that framework
framework_clusters = {
    'enterprise': 'mitre-attack-pattern',
    'ics': 'mitre-attack-pattern',
    'sparta': 'sparta-techniques',
}

session = requests.Session()
session.headers.update({'User-Agent': 'misp-galaxy/gen_mitre_d3fend.py'})


def fetch(path: str, cache_dir: str = None) -> dict:
    """GET <API_URL>/<path>, caching the response per ontology version."""
    cache_file = None
    if cache_dir:
        cache_file = os.path.join(cache_dir, path.replace('/', '_'))
        if os.path.exists(cache_file):
            with open(cache_file) as f:
                return json.load(f)
    r = session.get(f'{API_URL}/{path}', timeout=180)
    r.raise_for_status()   # the old code fed 404 HTML straight into r.json()
    data = r.json()
    if cache_file:
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(data, f)
    return data


def load_json(*path_parts: str) -> dict:
    with open(os.path.join(misp_dir, *path_parts)) as f:
        return json.load(f)


def save_json(data: dict, *path_parts: str) -> None:
    with open(os.path.join(misp_dir, *path_parts), 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things


def external_id_to_uuid(cluster_name: str) -> tuple[dict, set]:
    """external_id -> uuid of an existing cluster, plus the uuids it marks revoked."""
    result = {}
    revoked = set()
    for value in load_json('clusters', f'{cluster_name}.json')['values']:
        external_id = value.get('meta', {}).get('external_id')
        if external_id:
            result[external_id] = value['uuid']
            if value.get('revoked'):
                revoked.add(value['uuid'])
    return result, revoked


def label_of(value: dict) -> str:
    """The technique name of a cluster value, whichever naming the run that wrote it used.

    Values were named after the bare label until the galaxy moved to the
    "<name> - <id>" convention every other MITRE galaxy follows, so a value read
    back from the cluster can carry either form.
    """
    suffix = f" - {value['meta']['external_id']}"
    return value['value'][:-len(suffix)] if value['value'].endswith(suffix) else value['value']


def relation_keys(value: dict) -> set:
    """The (dest-uuid, type) pairs of a value, deduplicated."""
    return {(rel['dest-uuid'], rel['type']) for rel in value.get('related', [])}


def as_related(keys: set) -> list:
    return [{'dest-uuid': dest_uuid, 'type': rel_type} for dest_uuid, rel_type in sorted(keys)]


def find_successor(previous: dict, candidates: dict) -> tuple[float, str]:
    """Best match for a revoked technique among the ids that are new this run.

    Scored by the Jaccard ratio of the offensive mappings both carry: a renamed
    technique keeps nearly all of them, an unrelated one shares a handful.
    """
    keys = relation_keys(previous)
    if not keys:
        return 0.0, None
    best_ratio, best_id = 0.0, None
    for external_id, candidate in candidates.items():
        other = relation_keys(candidate)
        if not other:
            continue
        ratio = len(keys & other) / len(keys | other)
        if ratio > best_ratio:
            best_ratio, best_id = ratio, external_id
    return best_ratio, best_id


def walk_matrix(matrix: list) -> tuple[dict, dict]:
    """Flatten api/matrix.json into techniques and the tactic/phase ordering.

    The tree is tactic (depth 0) -> technique (depth 1) -> sub-technique (depth 2+),
    replacing the recursive subClassOf lookups of the previous version. Only the
    tactic is a grouping: a depth 1 node is a top-level technique in its own right
    - d3f:ObjectEviction is subClassOf d3f:DefensiveTechnique, exactly like the
    sub-techniques under it, and carries its own id, definition and mappings - so
    it becomes a cluster value and names the kill chain phase of its subtree.
    """
    techniques = {}          # d3fend-id -> {value, description, iri, kill_chain}
    kill_chain_order = {}    # tactic -> [phases]

    def walk(node, tactic, phase, depth):
        if depth == 1:
            phase = node['rdfs:label']
        if depth >= 1 and 'd3f:d3fend-id' in node:
            techniques[node['d3f:d3fend-id']] = {
                'value': node['rdfs:label'],
                'description': node['d3f:definition'],
                'iri': node['@id'],
                'kill_chain': f"{tactic}:{phase.replace(' ', '-')}",
            }
        elif depth >= 1:
            print(f"WARNING: no d3fend-id, skipping {node['@id']}")
        for child in node.get('children', []):
            walk(child, tactic, phase, depth + 1)

    for tactic_node in matrix:
        tactic = tactic_node['rdfs:label']
        kill_chain_order[tactic] = sorted(
            phase['rdfs:label'].replace(' ', '-') for phase in tactic_node.get('children', []))
        walk(tactic_node, tactic, None, 0)

    return techniques, kill_chain_order


def get_synonyms(item: dict) -> list:
    synonyms = item.get('d3f:synonym')
    if not synonyms:
        return []
    if isinstance(synonyms, str):
        return [synonyms]
    return list(synonyms)


def build_relations(technique_json: dict, resolvers: dict, unresolved: dict) -> list:
    """Convert the def_to_off bindings of one technique into related entries.

    D3FEND returns the cross product of defensive technique x offensive technique
    x digital artifact path, so the same (dest-uuid, type) shows up many times.
    Rows where def_tech_label differs from the queried technique belong to a
    parent phase, which is not a cluster value, and are dropped.
    """
    relations = set()
    for row in technique_json.get('def_to_off', {}).get('results', {}).get('bindings', []):
        if row['def_tech_label']['value'] != row['query_def_tech_label']['value']:
            continue
        framework = row['framework_key']['value']
        cluster_name = framework_clusters.get(framework)
        if not cluster_name:
            unresolved[framework].add(row['off_tech_id']['value'])
            continue
        dest_uuid = resolvers[cluster_name].get(row['off_tech_id']['value'])
        if not dest_uuid:
            unresolved[framework].add(row['off_tech_id']['value'])
            continue
        relations.add((dest_uuid, row['def_artifact_rel_label']['value']))
    return as_related(relations)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Convert MITRE D3FEND to a MISP galaxy.')
    parser.add_argument('-c', '--cache-dir', default=default_cache_dir,
                        help='directory to cache the API responses in (per ontology version)')
    parser.add_argument('--no-cache', action='store_true', help='always fetch from the API')
    parser.add_argument('-j', '--jobs', type=int, default=4, help='parallel requests')
    return parser.parse_args()


def load_resolvers() -> tuple[dict, set]:
    """external_id -> uuid per offensive cluster, and the uuids those clusters revoked."""
    resolvers = {}
    revoked_targets = set()
    for name in sorted(set(framework_clusters.values())):
        resolvers[name], revoked = external_id_to_uuid(name)
        revoked_targets |= revoked
    return resolvers, revoked_targets


def build_value(d3fend_id: str, technique: dict, synonyms: list, technique_json: dict,
                resolvers: dict, unresolved: dict) -> dict:
    """One cluster value, out of a technique and the mappings the API returned for it."""
    value = {
        'value': f"{technique['value']} - {d3fend_id}",
        'description': technique['description'],
        'uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), d3fend_id)),
        'meta': {
            'external_id': d3fend_id,
            'kill_chain': [technique['kill_chain']],
            'refs': [f"{TECHNIQUE_URL}/{technique['iri']}"],
        },
    }
    if synonyms:
        value['meta']['synonyms'] = sorted(synonyms)
    relations = build_relations(technique_json, resolvers, unresolved)
    if relations:
        value['related'] = relations
    return value


def build_values(techniques: dict, synonyms_of: dict, resolvers: dict, unresolved: dict,
                 cache_dir: str, jobs: int) -> list:
    """Fetch every technique - the API serves one at a time - and convert them."""
    def get_technique(d3fend_id: str) -> tuple:
        return d3fend_id, fetch(f"technique/{techniques[d3fend_id]['iri']}.json", cache_dir)

    with ThreadPoolExecutor(max_workers=jobs) as executor:
        return [build_value(d3fend_id, techniques[d3fend_id], synonyms_of.get(d3fend_id, []),
                            technique_json, resolvers, unresolved)
                for d3fend_id, technique_json in executor.map(get_technique, sorted(techniques))]


def carry_over_synonyms(new_values: dict, previous_values: dict) -> None:
    """Keep the old label of a technique renamed under a stable id searchable.

    The synonyms already recorded have to be carried over as well: they are
    rebuilt from upstream on every run, so a label kept here would be dropped
    again by the very next regeneration.
    """
    for external_id, value in new_values.items():
        previous = previous_values.get(external_id)
        if not previous:
            continue
        synonyms = set(value['meta'].get('synonyms', [])) | set(previous['meta'].get('synonyms', []))
        if label_of(previous) != label_of(value):
            # Only an upstream rename earns a synonym: moving every value to the
            # "<name> - <id>" convention is a migration, not 241 renames.
            print(f"Renamed: {label_of(previous)} -> {label_of(value)}")
            synonyms.add(previous['value'])
        if synonyms:
            value['meta']['synonyms'] = sorted(synonyms)


def link_successor(previous: dict, candidates: dict) -> None:
    """Point a revoked technique at the one that replaced it, where that is clear enough."""
    linked = {key for key in relation_keys(previous) if key[1] == 'revoked-by'}
    if linked:
        previous['related'] = as_related(linked)   # a successor set on an earlier run
        return
    ratio, successor_id = find_successor(previous, candidates)
    if ratio >= successor_link_ratio:
        successor = candidates[successor_id]
        print(f"    renamed upstream to {successor['value']} "
              f"(mapping overlap {ratio:.2f}), linking with revoked-by")
        previous['related'] = [{'dest-uuid': successor['uuid'], 'type': 'revoked-by'}]
        return
    if ratio >= successor_hint_ratio:
        print(f"WARNING: {previous['meta']['external_id']} may have been renamed to "
              f"{candidates[successor_id]['value']} "
              f"(mapping overlap {ratio:.2f}); add revoked-by by hand if it was")
    if previous.get('related'):
        previous['related'] = as_related(relation_keys(previous))


def drop_stale_kill_chain(value: dict, valid_kill_chains: set) -> None:
    """Drop phases the galaxy no longer declares - File-Eviction became Object-Eviction."""
    kill_chain = value['meta'].get('kill_chain', [])
    stale = [kc for kc in kill_chain if kc not in valid_kill_chains]
    if not stale:
        return
    print(f"    dropping kill_chain no longer in the galaxy: {', '.join(stale)}")
    remaining = [kc for kc in kill_chain if kc in valid_kill_chains]
    if remaining:
        value['meta']['kill_chain'] = remaining
    else:
        del value['meta']['kill_chain']


def revoke_missing(previous_values: dict, new_values: dict, kill_chain_order: dict) -> list:
    """Revoke - never delete - the techniques that disappeared upstream.

    Deleting them would orphan the tags of existing MISP events. A rename that
    moved the id lands here too, which is what link_successor is for.
    """
    valid_kill_chains = {f"{tactic}:{phase}"
                         for tactic, phases in kill_chain_order.items() for phase in phases}
    candidates = {external_id: value for external_id, value in new_values.items()
                  if external_id not in previous_values}
    revoked = []
    for external_id, previous in previous_values.items():
        if external_id in new_values:
            continue
        print(f"Revoked: {label_of(previous)} - {external_id}")
        previous['value'] = f"{label_of(previous)} - {external_id}"
        previous['revoked'] = True
        link_successor(previous, candidates)
        drop_stale_kill_chain(previous, valid_kill_chains)
        revoked.append(previous)
    return revoked


def report(cluster: dict, revoked_count: int, unresolved: dict, revoked_targets: set) -> None:
    relations_count = sum(len(value.get('related', [])) for value in cluster['values'])
    print(f"\n{len(cluster['values'])} values ({revoked_count} revoked), "
          f"{relations_count} relations")
    for framework, ids in sorted(unresolved.items()):
        print(f"WARNING: {len(ids)} unresolved {framework} technique(s): {', '.join(sorted(ids))}")
    stale_targets = sum(1 for value in cluster['values'] for rel in value.get('related', [])
                        if rel['dest-uuid'] in revoked_targets)
    if stale_targets:
        print(f"WARNING: {stale_targets} relation(s) point at a value the target cluster has "
              f"revoked; D3FEND still maps to them, so they are kept - check if that diverges")
    print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh.")


def main() -> None:
    args = parse_args()

    version_json = fetch('version.json')
    ontology_version = version_json['ontology_version']
    cache_dir = None if args.no_cache else os.path.join(args.cache_dir, ontology_version)
    print(f"D3FEND {ontology_version} released {version_json['release_date']} "
          f"({version_json['ontology_hash_sha256']})")

    techniques, kill_chain_order = walk_matrix(fetch('matrix.json', cache_dir))
    synonyms_of = {item['d3f:d3fend-id']: get_synonyms(item)
                   for item in fetch('technique/all.json', cache_dir)['@graph']
                   if 'd3f:d3fend-id' in item}
    print(f"{len(techniques)} techniques in "
          f"{sum(len(phases) for phases in kill_chain_order.values())} phases")

    resolvers, revoked_targets = load_resolvers()
    unresolved = defaultdict(set)
    values = build_values(techniques, synonyms_of, resolvers, unresolved, cache_dir, args.jobs)
    new_values = {value['meta']['external_id']: value for value in values}

    cluster = load_json('clusters', galaxy_fname)
    previous_values = {value['meta']['external_id']: value
                       for value in cluster['values'] if value.get('meta', {}).get('external_id')}
    carry_over_synonyms(new_values, previous_values)
    revoked = revoke_missing(previous_values, new_values, kill_chain_order)

    cluster['values'] = sorted(values + revoked, key=lambda value: value['meta']['external_id'])
    cluster['version'] += 1
    save_json(cluster, 'clusters', galaxy_fname)

    galaxy = load_json('galaxies', galaxy_fname)
    galaxy['kill_chain_order'] = kill_chain_order
    galaxy['version'] += 1
    save_json(galaxy, 'galaxies', galaxy_fname)

    report(cluster, len(revoked), unresolved, revoked_targets)


if __name__ == '__main__':
    main()
