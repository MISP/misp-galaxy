#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    Convert the VERIS framework taxonomy into a MISP galaxy/cluster.
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
from typing import Any

import requests

VERIS_ENUM_URL = 'https://raw.githubusercontent.com/vz-risk/veris/master/verisc-enum.json'
VERIS_LABELS_URL = 'https://raw.githubusercontent.com/vz-risk/veris/master/verisc-labels.json'
VERIS_SOURCE_URL = 'https://github.com/vz-risk/veris'
UUID_NAMESPACE = uuid.UUID('9a5af9ab-1f67-4f68-b4ee-1e8e2d7baf4b')


@dataclass
class VerisNode:
    path: tuple[str, ...]
    value: str
    description: str | None
    parent_path: tuple[str, ...] | None
    node_type: str


def to_uuid(path: tuple[str, ...]) -> str:
    return str(uuid.uuid5(UUID_NAMESPACE, '.'.join(path)))


def titleize_key(text: str) -> str:
    return re.sub(r'\s+', ' ', text.replace('_', ' ').replace('.', ' ')).strip().title()


def normalize(text: str) -> str:
    lowered = text.lower()
    cleaned = re.sub(r'[^a-z0-9]+', ' ', lowered)
    return re.sub(r'\s+', ' ', cleaned).strip()


def fetch_json(url: str, timeout: int) -> dict[str, Any]:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def get_label(labels: Any, key: str) -> str | None:
    if isinstance(labels, dict):
        value = labels.get(key)
        if isinstance(value, str):
            return value.strip() or None
    return None


def extract_nodes(enum_data: dict[str, Any], label_data: dict[str, Any]) -> list[VerisNode]:
    nodes: list[VerisNode] = []

    def walk(current: Any, labels: Any, path: tuple[str, ...], parent_path: tuple[str, ...] | None) -> None:
        if isinstance(current, dict):
            if path:
                key = path[-1]
                nodes.append(
                    VerisNode(
                        path=path,
                        value=titleize_key(key),
                        description=get_label(labels, key),
                        parent_path=parent_path,
                        node_type='category',
                    )
                )

            for key, subvalue in current.items():
                sublabels = labels.get(key, {}) if isinstance(labels, dict) else {}
                walk(subvalue, sublabels, path + (key,), path if path else None)

        elif isinstance(current, list):
            for item in current:
                if not isinstance(item, str):
                    continue
                label = get_label(labels, item)
                nodes.append(
                    VerisNode(
                        path=path + (item,),
                        value=item,
                        description=label,
                        parent_path=path if path else None,
                        node_type='value',
                    )
                )

    walk(enum_data, label_data, tuple(), None)
    return nodes


def load_other_cluster_values(clusters_dir: str) -> dict[str, list[dict[str, str]]]:
    index: dict[str, list[dict[str, str]]] = {}

    for filename in os.listdir(clusters_dir):
        if not filename.endswith('.json'):
            continue
        cluster_path = os.path.join(clusters_dir, filename)
        with open(cluster_path, 'r') as handle:
            cluster_data = json.load(handle)

        cluster_type = cluster_data.get('type', '')
        if cluster_type == 'veris-framework':
            continue

        for value in cluster_data.get('values', []):
            value_uuid = value.get('uuid') or value.get('meta', {}).get('uuid')
            value_name = value.get('value')
            if not value_uuid or not value_name:
                continue

            candidates = [value_name]
            meta = value.get('meta', {})
            if isinstance(meta, dict):
                candidates.extend(s for s in meta.get('synonyms', []) if isinstance(s, str))

            for candidate in candidates:
                key = normalize(candidate)
                if not key:
                    continue
                index.setdefault(key, []).append(
                    {
                        'uuid': value_uuid,
                        'type': cluster_type,
                        'value': value_name,
                    }
                )

    return index


def build_cluster_values(
    nodes: list[VerisNode],
    external_index: dict[str, list[dict[str, str]]],
    max_cross_links: int,
) -> list[dict[str, Any]]:
    entries_by_path: dict[tuple[str, ...], dict[str, Any]] = {}

    for node in nodes:
        meta = {
            'path': '.'.join(node.path),
            'level': str(len(node.path)),
            'node_type': node.node_type,
            'top_level_domain': node.path[0],
            'source': VERIS_SOURCE_URL,
        }

        if node.parent_path:
            meta['parent_path'] = '.'.join(node.parent_path)

        entry: dict[str, Any] = {
            'value': node.value,
            'uuid': to_uuid(node.path),
            'meta': meta,
        }

        if node.description:
            entry['description'] = node.description

        entries_by_path[node.path] = entry

    for node in nodes:
        entry = entries_by_path[node.path]
        related: list[dict[str, Any]] = []

        if node.parent_path and node.parent_path in entries_by_path:
            related.append(
                {
                    'dest-uuid': entries_by_path[node.parent_path]['uuid'],
                    'type': 'part-of',
                }
            )

        matches = external_index.get(normalize(node.value), [])
        seen_dest = set()
        for match in matches:
            if match['uuid'] in seen_dest:
                continue
            related.append(
                {
                    'dest-uuid': match['uuid'],
                    'type': 'similar',
                    'tags': [
                        'estimative-language:likelihood-probability="likely"',
                        f'misp-galaxy:type="{match["type"]}"',
                    ],
                }
            )
            seen_dest.add(match['uuid'])
            if len(seen_dest) >= max_cross_links:
                break

        if related:
            entry['related'] = related

    return sorted(entries_by_path.values(), key=lambda e: (e['meta']['path'], e['value']))


def write_output(output_dir: str, values: list[dict[str, Any]]) -> None:
    galaxy = {
        'name': 'VERIS Framework',
        'description': 'VERIS taxonomy for describing cybersecurity incidents, including categories and enumerated values.',
        'icon': 'sitemap',
        'namespace': 'veris',
        'type': 'veris-framework',
        'uuid': str(uuid.uuid5(UUID_NAMESPACE, 'galaxy:veris-framework')),
        'version': 1,
    }

    cluster = {
        'authors': ['Verizon DBIR Team', 'MISP Project'],
        'category': 'framework',
        'description': galaxy['description'],
        'name': galaxy['name'],
        'source': VERIS_SOURCE_URL,
        'type': galaxy['type'],
        'uuid': str(uuid.uuid5(UUID_NAMESPACE, 'cluster:veris-framework')),
        'version': 1,
        'values': values,
    }

    galaxy_path = os.path.join(output_dir, 'galaxies', 'veris-framework.json')
    cluster_path = os.path.join(output_dir, 'clusters', 'veris-framework.json')

    with open(galaxy_path, 'w') as handle:
        json.dump(galaxy, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write('\n')

    with open(cluster_path, 'w') as handle:
        json.dump(cluster, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write('\n')


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate a VERIS-based MISP galaxy and cluster.')
    parser.add_argument('--output-dir', default='..', help='misp-galaxy repository root (default: ../ from tools/)')
    parser.add_argument('--timeout', type=int, default=60, help='HTTP timeout in seconds (default: 60)')
    parser.add_argument('--max-cross-links', type=int, default=10, help='Maximum number of cross-galaxy similar links per node')
    args = parser.parse_args()

    enum_data = fetch_json(VERIS_ENUM_URL, timeout=args.timeout)
    label_data = fetch_json(VERIS_LABELS_URL, timeout=args.timeout)

    nodes = extract_nodes(enum_data, label_data)

    clusters_dir = os.path.join(args.output_dir, 'clusters')
    external_index = load_other_cluster_values(clusters_dir)

    values = build_cluster_values(nodes, external_index, max_cross_links=max(0, args.max_cross_links))
    write_output(args.output_dir, values)

    print(f'Wrote galaxies/veris-framework.json and clusters/veris-framework.json with {len(values)} entries.')


if __name__ == '__main__':
    main()
