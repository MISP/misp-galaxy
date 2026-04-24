#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    Convert Aerospace SPARTA STIX data to MISP galaxy/cluster files.
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
from dataclasses import dataclass

import requests

VERSIONS_URL = 'https://sparta.aerospace.org/resources/versions'
DOWNLOAD_TEMPLATE = 'https://sparta.aerospace.org/download/STIX?f=sparta_data_v{version}.json'
LATEST_DOWNLOAD_URL = 'https://sparta.aerospace.org/download/STIX?f=latest'
SPARTA_SOURCE_URL = 'https://sparta.aerospace.org/'
UUID_NAMESPACE = uuid.UUID('89c45e8f-0fb7-4ac0-a7f5-2517c4a86f2f')
KILL_CHAIN_NAME = 'sparta'


@dataclass(frozen=True)
class GalaxySpec:
    filename: str
    galaxy_type: str
    name: str
    description: str
    category: str


SPECS = {
    'tactics': GalaxySpec(
        filename='sparta-tactics.json',
        galaxy_type='sparta-tactics',
        name='SPARTA Tactics',
        description='SPARTA tactics published by The Aerospace Corporation.',
        category='tool'
    ),
    'techniques': GalaxySpec(
        filename='sparta-techniques.json',
        galaxy_type='sparta-techniques',
        name='SPARTA Techniques',
        description='SPARTA techniques and sub-techniques derived from the official STIX feed.',
        category='tool'
    ),
    'mitigations': GalaxySpec(
        filename='sparta-mitigations.json',
        galaxy_type='sparta-mitigations',
        name='SPARTA Mitigations',
        description='SPARTA countermeasures derived from the official STIX feed.',
        category='tool'
    ),
}


def stix_id_to_uuid(stix_id: str) -> str:
    match = re.search(r'--([0-9a-f-]{36})$', stix_id)
    if match:
        return match.group(1)
    return str(uuid.uuid5(UUID_NAMESPACE, stix_id))


def normalize_version(version: str) -> tuple[int, ...]:
    return tuple(int(p) for p in version.split('.'))


def find_latest_version(timeout: int = 30) -> str:
    response = requests.get(VERSIONS_URL, timeout=timeout)
    response.raise_for_status()
    matches = re.findall(r'SPARTA v(\d+(?:\.\d+)*)', response.text)
    if not matches:
        raise RuntimeError(f'Unable to extract a SPARTA version from {VERSIONS_URL}')
    unique_versions = sorted(set(matches), key=normalize_version)
    return unique_versions[-1]


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


def meta_with_refs_and_external_id(item: dict) -> dict:
    meta = {}
    refs = extract_refs(item)
    if refs:
        meta['refs'] = refs
    external_id = first_external_id(item)
    if external_id:
        meta['external_id'] = external_id
    return meta


def parse_bundle(bundle: dict) -> tuple[list[dict], dict[str, dict], dict[str, dict], list[str], list[dict], list[dict]]:
    objects = bundle.get('objects', [])
    tactics_by_id = {}
    techniques_by_id = {}
    mitigations_by_id = {}

    for item in objects:
        if item.get('x_mitre_deprecated') or item.get('revoked'):
            continue
        item_type = item.get('type')
        if item_type == 'x-mitre-tactic':
            tactics_by_id[item['id']] = item
        elif item_type == 'attack-pattern':
            techniques_by_id[item['id']] = item
        elif item_type == 'course-of-action':
            mitigations_by_id[item['id']] = item

    matrix_order = []
    for item in objects:
        if item.get('type') != 'x-mitre-matrix':
            continue
        if item.get('x_mitre_deprecated') or item.get('revoked'):
            continue
        for tactic_id in item.get('tactic_refs', []):
            tactic = tactics_by_id.get(tactic_id)
            if not tactic:
                continue
            shortname = tactic.get('x_mitre_shortname', tactic.get('name', '').lower().replace(' ', '-'))
            if shortname and shortname not in matrix_order:
                matrix_order.append(shortname)

    if not matrix_order:
        matrix_order = [
            t.get('x_mitre_shortname', t.get('name', '').lower().replace(' ', '-'))
            for t in sorted(tactics_by_id.values(), key=lambda v: (first_external_id(v) or '', v.get('name', '')))
        ]

    relationships = [
        item for item in objects
        if item.get('type') == 'relationship'
        and not item.get('x_mitre_deprecated')
        and not item.get('revoked')
    ]

    return objects, tactics_by_id, techniques_by_id, matrix_order, list(mitigations_by_id.values()), relationships


def build_tactics_cluster(tactics_by_id: dict[str, dict]) -> list[dict]:
    values = []
    for tactic in tactics_by_id.values():
        shortname = tactic.get('x_mitre_shortname', tactic.get('name', '').lower().replace(' ', '-'))
        meta = meta_with_refs_and_external_id(tactic)
        if shortname:
            meta['shortname'] = shortname

        entry = {
            'value': tactic.get('name', ''),
            'uuid': stix_id_to_uuid(tactic['id']),
        }
        if tactic.get('description'):
            entry['description'] = tactic['description'].strip()
        if meta:
            entry['meta'] = meta
        values.append(entry)

    return sorted(values, key=lambda e: (e.get('meta', {}).get('external_id', ''), e['value']))


def build_techniques_cluster(
    techniques_by_id: dict[str, dict],
    tactics_by_id: dict[str, dict],
) -> list[dict]:
    tactic_by_shortname = {
        t.get('x_mitre_shortname', t.get('name', '').lower().replace(' ', '-')): t
        for t in tactics_by_id.values()
    }

    values = []
    for technique in techniques_by_id.values():
        meta = meta_with_refs_and_external_id(technique)

        kill_chain = []
        for phase in technique.get('kill_chain_phases', []):
            phase_name = phase.get('phase_name')
            if not phase_name:
                continue
            tactic = tactic_by_shortname.get(phase_name)
            mapped_name = tactic.get('x_mitre_shortname', phase_name) if tactic else phase_name
            chain = f'{KILL_CHAIN_NAME}:{mapped_name}'
            if chain not in kill_chain:
                kill_chain.append(chain)
        if kill_chain:
            meta['kill_chain'] = kill_chain

        if technique.get('x_mitre_platforms'):
            meta['mitre_platforms'] = technique['x_mitre_platforms']

        if technique.get('x_mitre_is_subtechnique'):
            meta['is_subtechnique'] = True

        entry = {
            'value': technique.get('name', ''),
            'uuid': stix_id_to_uuid(technique['id']),
        }
        if technique.get('description'):
            entry['description'] = technique['description'].strip()
        if meta:
            entry['meta'] = meta
        values.append(entry)

    return sorted(values, key=lambda e: (e.get('meta', {}).get('external_id', ''), e['value']))


def build_mitigations_cluster(mitigations: list[dict], relationships: list[dict]) -> list[dict]:
    mitigated_by_coa = {}
    for relation in relationships:
        if relation.get('relationship_type') != 'mitigates':
            continue
        source_ref = relation.get('source_ref', '')
        target_ref = relation.get('target_ref', '')
        if not source_ref.startswith('course-of-action--') or not target_ref.startswith('attack-pattern--'):
            continue
        mitigated_by_coa.setdefault(source_ref, set()).add(target_ref)

    values = []
    for mitigation in mitigations:
        meta = meta_with_refs_and_external_id(mitigation)

        mitigates = sorted(stix_id_to_uuid(t) for t in mitigated_by_coa.get(mitigation['id'], set()))
        if mitigates:
            meta['mitigates'] = mitigates

        entry = {
            'value': mitigation.get('name', ''),
            'uuid': stix_id_to_uuid(mitigation['id']),
        }
        if mitigation.get('description'):
            entry['description'] = mitigation['description'].strip()
        if meta:
            entry['meta'] = meta
        values.append(entry)

    return sorted(values, key=lambda e: (e.get('meta', {}).get('external_id', ''), e['value']))


def write_galaxy_and_cluster(
    output_dir: str,
    spec: GalaxySpec,
    values: list[dict],
    matrix_order: list[str] | None,
    source: str,
) -> None:
    galaxy = {
        'name': spec.name,
        'description': spec.description,
        'icon': 'map' if matrix_order else 'shield-alt',
        'namespace': 'sparta',
        'type': spec.galaxy_type,
        'uuid': str(uuid.uuid5(UUID_NAMESPACE, f'galaxy:{spec.galaxy_type}')),
        'version': 1,
    }
    if matrix_order:
        galaxy['kill_chain_order'] = {KILL_CHAIN_NAME: matrix_order}

    cluster = {
        'authors': ['The Aerospace Corporation'],
        'category': spec.category,
        'description': spec.description,
        'name': spec.name,
        'source': source,
        'type': spec.galaxy_type,
        'uuid': str(uuid.uuid5(UUID_NAMESPACE, f'cluster:{spec.galaxy_type}')),
        'version': 1,
        'values': values,
    }

    galaxy_path = os.path.join(output_dir, 'galaxies', spec.filename)
    cluster_path = os.path.join(output_dir, 'clusters', spec.filename)

    with open(galaxy_path, 'w') as f_galaxy:
        json.dump(galaxy, f_galaxy, indent=2, sort_keys=True, ensure_ascii=False)
        f_galaxy.write('\n')

    with open(cluster_path, 'w') as f_cluster:
        json.dump(cluster, f_cluster, indent=2, sort_keys=True, ensure_ascii=False)
        f_cluster.write('\n')


def fetch_bundle(url: str, timeout: int) -> dict:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description='Create MISP SPARTA galaxies/clusters from Aerospace SPARTA STIX data.')
    parser.add_argument('--output-dir', default='..', help='misp-galaxy repository root (default: ../ from tools/)')
    parser.add_argument('--timeout', type=int, default=60, help='HTTP timeout in seconds (default: 60)')
    parser.add_argument('--version', help='SPARTA version to download (e.g. 3.2). If omitted, auto-detect latest from the versions page.')
    parser.add_argument('--stix-url', help='Override STIX URL. When set, --version discovery is skipped.')
    args = parser.parse_args()

    source = SPARTA_SOURCE_URL
    if args.stix_url:
        stix_url = args.stix_url
    else:
        version = args.version
        if not version:
            version = find_latest_version(timeout=args.timeout)
        stix_url = DOWNLOAD_TEMPLATE.format(version=version)
        source = f'{SPARTA_SOURCE_URL}resources/versions'

    try:
        bundle = fetch_bundle(stix_url, timeout=args.timeout)
    except requests.HTTPError:
        if args.stix_url or args.version:
            raise
        bundle = fetch_bundle(LATEST_DOWNLOAD_URL, timeout=args.timeout)

    _, tactics_by_id, techniques_by_id, matrix_order, mitigations, relationships = parse_bundle(bundle)

    write_galaxy_and_cluster(
        output_dir=args.output_dir,
        spec=SPECS['tactics'],
        values=build_tactics_cluster(tactics_by_id),
        matrix_order=matrix_order,
        source=source,
    )
    write_galaxy_and_cluster(
        output_dir=args.output_dir,
        spec=SPECS['techniques'],
        values=build_techniques_cluster(techniques_by_id, tactics_by_id),
        matrix_order=matrix_order,
        source=source,
    )
    write_galaxy_and_cluster(
        output_dir=args.output_dir,
        spec=SPECS['mitigations'],
        values=build_mitigations_cluster(mitigations, relationships),
        matrix_order=None,
        source=source,
    )

    print('Wrote galaxies/clusters for SPARTA tactics, techniques, and mitigations.')


if __name__ == '__main__':
    main()
