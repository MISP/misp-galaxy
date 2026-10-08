#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    Convert MITRE F3 STIX data to a MISP galaxy/cluster matrix.
#    Copyright (C) 2026 MISP Project
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.

from __future__ import annotations

import argparse
import json
import os
import re
import uuid

import requests

# CTID moved the Fight Fraud Framework from /fraud to /fightfraud: the directory
# 301s, the JSON under it does not. The site serves both a versioned
# f3-stix-v<x.y>.json - the path the SPA hardcodes - and this unversioned alias to
# the current release. Fetch the alias: pinning the version would leave the galaxy
# silently stale at the next release, and there is no archive to fall back on
# (f3-stix-v1.0.json is already gone). The release fetched is reported instead.
SOURCE_URL = 'https://ctid.mitre.org/fightfraud/f3-stix.json'
SITE_BASE = 'https://ctid.mitre.org/fightfraud'
# The site is a hash-routed SPA; the route is singular, and its parameter is the
# external id. Upstream's own external_references still carry the pre-move
# /fraud/techniques/<id> URLs, which 404, so the refs have to be built here.
TECHNIQUE_URL = SITE_BASE + '/#/technique/{}'

GALAXY_FILENAME = 'mitre-fraud-framework.json'
KILL_CHAIN_NAME = 'mitre-f3'
ATTACK_CLUSTER = 'mitre-attack-pattern'
TAG_ALMOST_CERTAIN = 'estimative-language:likelihood-probability="almost-certain"'
UUID_NAMESPACE = uuid.UUID('f0a74a66-c60e-4be0-bd9f-bd2d4c441f8f')

misp_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def stix_id_to_uuid(stix_id: str) -> str:
    match = re.search(r'--([0-9a-f-]{36})$', stix_id)
    if match:
        return match.group(1)
    return str(uuid.uuid5(UUID_NAMESPACE, stix_id))


def first_external_id(item: dict) -> str | None:
    for reference in item.get('external_references', []):
        external_id = reference.get('external_id')
        if external_id:
            return external_id
    return None


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
            # "<name> - <id>" convention is a migration, not 123 renames.
            print(f"Renamed: {label_of(previous)} -> {label_of(value)}")
            synonyms.add(previous['value'])
        if synonyms:
            value['meta']['synonyms'] = sorted(synonyms)


def parse_tactics(objects: list[dict]) -> tuple[dict[str, dict], list[str]]:
    tactics_by_id = {}
    for item in objects:
        if item.get('type') != 'x-mitre-tactic':
            continue
        if item.get('x_mitre_deprecated') or item.get('revoked'):
            continue
        tactics_by_id[item['id']] = {
            'name': item.get('name', ''),
            'shortname': item.get('x_mitre_shortname', item.get('name', '').lower().replace(' ', '-')),
            'external_id': first_external_id(item),
        }

    matrix_order = []
    for item in objects:
        if item.get('type') != 'x-mitre-matrix':
            continue
        if item.get('x_mitre_deprecated') or item.get('revoked'):
            continue
        for tactic_id in item.get('tactic_refs', []):
            tactic = tactics_by_id.get(tactic_id)
            if tactic and tactic['shortname'] not in matrix_order:
                matrix_order.append(tactic['shortname'])

    if not matrix_order:
        matrix_order = [
            tactic['shortname']
            for tactic in sorted(
                tactics_by_id.values(),
                key=lambda x: (x['external_id'] is None, x['external_id'] or x['name'])
            )
        ]

    return tactics_by_id, matrix_order


def subtechnique_parents(objects: list[dict]) -> dict[str, str]:
    """STIX id of a sub-technique -> STIX id of its parent."""
    return {
        item['source_ref']: item['target_ref']
        for item in objects
        if item.get('type') == 'relationship'
        and item.get('relationship_type') == 'subtechnique-of'
        and not (item.get('x_mitre_deprecated') or item.get('revoked'))
    }


def live_techniques(objects: list[dict]):
    """The attack-pattern objects upstream still stands behind."""
    for item in objects:
        if item.get('type') != 'attack-pattern':
            continue
        if item.get('x_mitre_deprecated') or item.get('revoked'):
            continue
        yield item


def build_kill_chain(item: dict, external_id: str, shortnames: set) -> list[str]:
    """The tactics of a technique, in upstream order, deduplicated."""
    kill_chain = []
    for phase in item.get('kill_chain_phases', []):
        phase_name = phase.get('phase_name')
        if not phase_name:
            continue
        if phase_name not in shortnames:
            print(f"WARNING: {external_id} sits in tactic {phase_name}, "
                  f"which the matrix does not declare")
        chain = f'{KILL_CHAIN_NAME}:{phase_name}'
        if chain not in kill_chain:
            kill_chain.append(chain)
    return kill_chain


def build_related(item: dict, external_id: str, parent_of: dict[str, str],
                  attack_uuid: dict[str, str], unresolved: set) -> tuple[list[dict], str | None]:
    """The relationships of a technique, and the ATT&CK id to record on it, if any."""
    related = []
    parent = parent_of.get(item['id'])
    if parent:
        related.append({'dest-uuid': stix_id_to_uuid(parent), 'type': 'subtechnique-of'})

    # F3 reuses ATT&CK techniques where they apply to fraud, and mints its own
    # uuid for each, so the ATT&CK galaxy holds the same technique under a
    # different uuid. Link the two rather than deduplicating them: every
    # inbound reference this cluster already has lands on one of these values.
    # Upstream flags them isAttack on the site; in the STIX bundle the T####
    # external id is the only signal, and it selects exactly the same set.
    attack_id = None
    if external_id.startswith('T'):
        dest = attack_uuid.get(external_id)
        if dest:
            attack_id = external_id
            related.append({'dest-uuid': dest, 'type': 'related-to',
                            'tags': [TAG_ALMOST_CERTAIN]})
        else:
            # An id F3 minted inside the ATT&CK namespace that ATT&CK does not
            # have, or an ATT&CK galaxy older than the F3 release.
            unresolved.add(external_id)

    return sorted(related, key=lambda rel: (rel['type'], rel['dest-uuid'])), attack_id


def build_values(objects: list[dict], tactics_by_id: dict[str, dict], parent_of: dict[str, str],
                 attack_uuid: dict[str, str], unresolved: set) -> list[dict]:
    shortnames = {tactic['shortname'] for tactic in tactics_by_id.values()}
    values = []
    for item in live_techniques(objects):
        external_id = first_external_id(item)
        if not external_id:
            print(f"WARNING: {item['id']} has no external id, skipped")
            continue

        meta = {
            'external_id': external_id,
            'refs': [TECHNIQUE_URL.format(external_id)],
        }
        kill_chain = build_kill_chain(item, external_id, shortnames)
        if kill_chain:
            meta['kill_chain'] = kill_chain

        related, attack_id = build_related(item, external_id, parent_of, attack_uuid, unresolved)
        if attack_id:
            meta['mitre_attack_id'] = attack_id

        value = {
            'value': f"{item['name']} - {external_id}",
            'uuid': stix_id_to_uuid(item['id']),
            'meta': meta,
        }
        if item.get('description'):
            value['description'] = item['description'].strip()
        if related:
            value['related'] = related

        values.append(value)

    return sorted(values, key=lambda value: (value['meta']['external_id'], value['value']))


def check_parents(values: list[dict]) -> None:
    """Every subtechnique-of edge has to land on a value of this cluster."""
    known = {value['uuid'] for value in values}
    dangling = [(value['value'], rel['dest-uuid'])
                for value in values for rel in value.get('related', [])
                if rel['type'] == 'subtechnique-of' and rel['dest-uuid'] not in known]
    if dangling:
        raise SystemExit(f"ERROR: {len(dangling)} subtechnique-of edge(s) point outside "
                         f"the cluster: {dangling}")


def report(cluster: dict, previous_values: dict, new_values: dict,
           unresolved: set, revoked_targets: set) -> None:
    relations = [rel for value in cluster['values'] for rel in value.get('related', [])]
    by_type = {}
    for rel in relations:
        by_type[rel['type']] = by_type.get(rel['type'], 0) + 1
    print(f"\n{len(cluster['values'])} values, {len(relations)} relations "
          f"({', '.join(f'{count} {name}' for name, count in sorted(by_type.items()))})")

    if unresolved:
        print(f"WARNING: {len(unresolved)} technique(s) carry an ATT&CK id that is not in "
              f"{ATTACK_CLUSTER}: {', '.join(sorted(unresolved))}")
    stale = sum(1 for rel in relations if rel['dest-uuid'] in revoked_targets)
    if stale:
        print(f"WARNING: {stale} relation(s) point at a revoked {ATTACK_CLUSTER} value")
    gone = sorted(set(previous_values) - set(new_values))
    if gone:
        # Deleting them would orphan the tags of existing MISP events; revoking
        # them properly is not implemented yet, so make the loss impossible to miss.
        print(f"WARNING: {len(gone)} technique(s) disappeared upstream and were dropped, "
              f"not revoked: {', '.join(gone)}")


def main() -> None:
    parser = argparse.ArgumentParser(description='Create MISP matrix galaxy files for the MITRE F3 Fraud Framework.')
    parser.add_argument('--url', default=SOURCE_URL, help='STIX bundle URL')
    parser.add_argument('--output-dir', help='misp-galaxy repository root (default: the one this script lives in)')
    args = parser.parse_args()

    if args.output_dir:
        global misp_dir
        misp_dir = args.output_dir

    response = requests.get(args.url, timeout=30)
    response.raise_for_status()
    bundle = response.json()

    objects = bundle.get('objects', [])
    collection = next((item for item in objects if item.get('type') == 'x-mitre-collection'), {})
    print(f"F3 {collection.get('x_mitre_version', 'of an unreported version')} "
          f"({len(objects)} STIX objects) from {args.url}")

    tactics_by_id, matrix_order = parse_tactics(objects)
    attack_uuid, revoked_targets = external_id_to_uuid(ATTACK_CLUSTER)
    values = build_values(objects, tactics_by_id, subtechnique_parents(objects),
                          attack_uuid, unresolved := set())
    check_parents(values)

    # Both files are curated in the repository - name, description, uuid and the
    # version counter included - so read them back and edit, never rebuild.
    cluster = load_json('clusters', GALAXY_FILENAME)
    previous_values = {value['meta']['external_id']: value for value in cluster['values']
                       if value.get('meta', {}).get('external_id')}
    new_values = {value['meta']['external_id']: value for value in values}
    carry_over_synonyms(new_values, previous_values)

    cluster['values'] = values
    cluster['source'] = SITE_BASE
    cluster['version'] += 1
    save_json(cluster, 'clusters', GALAXY_FILENAME)

    galaxy = load_json('galaxies', GALAXY_FILENAME)
    galaxy['kill_chain_order'] = {KILL_CHAIN_NAME: matrix_order}
    galaxy['version'] += 1
    save_json(galaxy, 'galaxies', GALAXY_FILENAME)

    print(f"{len(matrix_order)} tactics: {', '.join(matrix_order)}")
    report(cluster, previous_values, new_values, unresolved, revoked_targets)


if __name__ == '__main__':
    main()
