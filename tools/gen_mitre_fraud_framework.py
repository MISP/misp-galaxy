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

SOURCE_URL = 'https://ctid.mitre.org/fraud/f3-stix.json'
GALAXY_FILENAME = 'mitre-fraud-framework.json'
GALAXY_TYPE = 'mitre-fraud-framework'
KILL_CHAIN_NAME = 'mitre-f3'
UUID_NAMESPACE = uuid.UUID('f0a74a66-c60e-4be0-bd9f-bd2d4c441f8f')


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


def extract_refs(item: dict) -> list[str]:
    refs = []
    for reference in item.get('external_references', []):
        url = reference.get('url')
        if url and url not in refs:
            refs.append(url)
    return refs


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


def build_cluster(objects: list[dict], tactics_by_id: dict[str, dict]) -> list[dict]:
    values = []
    for item in objects:
        if item.get('type') != 'attack-pattern':
            continue
        if item.get('x_mitre_deprecated') or item.get('revoked'):
            continue

        meta = {}
        refs = extract_refs(item)
        if refs:
            meta['refs'] = refs

        external_id = first_external_id(item)
        if external_id:
            meta['external_id'] = external_id

        kill_chain = []
        for phase in item.get('kill_chain_phases', []):
            phase_name = phase.get('phase_name')
            if not phase_name:
                continue
            tactic = next((t for t in tactics_by_id.values() if t['shortname'] == phase_name), None)
            mapped_name = tactic['shortname'] if tactic else phase_name
            chain = f"{KILL_CHAIN_NAME}:{mapped_name}"
            if chain not in kill_chain:
                kill_chain.append(chain)
        if kill_chain:
            meta['kill_chain'] = kill_chain

        if item.get('x_mitre_platforms'):
            meta['mitre_platforms'] = item['x_mitre_platforms']

        cluster_value = {
            'value': item['name'],
            'uuid': stix_id_to_uuid(item['id']),
        }
        if item.get('description'):
            cluster_value['description'] = item['description'].strip()
        if meta:
            cluster_value['meta'] = meta

        values.append(cluster_value)

    def sort_key(entry: dict) -> tuple[str, str]:
        ext_id = entry.get('meta', {}).get('external_id', '')
        return (ext_id, entry['value'])

    return sorted(values, key=sort_key)


def main() -> None:
    parser = argparse.ArgumentParser(description='Create MISP matrix galaxy files for the MITRE F3 Fraud Framework.')
    parser.add_argument('--url', default=SOURCE_URL, help='STIX bundle URL')
    parser.add_argument('--output-dir', default='..', help='misp-galaxy repository root (default: ../ from tools/)')
    args = parser.parse_args()

    response = requests.get(args.url, timeout=30)
    response.raise_for_status()
    bundle = response.json()

    objects = bundle.get('objects', [])
    tactics_by_id, matrix_order = parse_tactics(objects)
    cluster_values = build_cluster(objects, tactics_by_id)

    galaxy = {
        'name': 'MITRE Fight Fraud Framework',
        'description': 'MITRE Fight Fraud Framework (F3) matrix of fraud techniques.',
        'icon': 'map',
        'namespace': 'mitre',
        'type': GALAXY_TYPE,
        'uuid': str(uuid.uuid5(UUID_NAMESPACE, f'galaxy:{GALAXY_TYPE}')),
        'version': 1,
        'kill_chain_order': {
            KILL_CHAIN_NAME: matrix_order
        }
    }

    cluster = {
        'authors': ['MITRE'],
        'category': 'attack-pattern',
        'description': galaxy['description'],
        'name': galaxy['name'],
        'source': 'https://ctid.mitre.org/fraud/',
        'type': GALAXY_TYPE,
        'uuid': str(uuid.uuid5(UUID_NAMESPACE, f'cluster:{GALAXY_TYPE}')),
        'version': 1,
        'values': cluster_values,
    }

    galaxy_path = os.path.join(args.output_dir, 'galaxies', GALAXY_FILENAME)
    cluster_path = os.path.join(args.output_dir, 'clusters', GALAXY_FILENAME)

    with open(galaxy_path, 'w') as f_galaxy:
        json.dump(galaxy, f_galaxy, indent=2, sort_keys=True, ensure_ascii=False)
        f_galaxy.write('\n')

    with open(cluster_path, 'w') as f_cluster:
        json.dump(cluster, f_cluster, indent=2, sort_keys=True, ensure_ascii=False)
        f_cluster.write('\n')

    print(f'Wrote {galaxy_path} and {cluster_path}')


if __name__ == '__main__':
    main()
