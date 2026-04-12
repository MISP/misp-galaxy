#!/usr/bin/env python3
"""Generate a GraphML export for all MISP galaxies and clusters.

The graph contains:
- One node per galaxy definition (`galaxies/*.json`)
- One node per cluster value (`clusters/*.json`)
- Optional explicit edges from `cluster.related`
- Optional inferred edges across galaxy types when values/synonyms match
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Galaxy:
    uuid: str
    type: str
    name: str
    description: str


@dataclass(frozen=True)
class Cluster:
    node_id: str
    uuid: str
    value: str
    galaxy_type: str
    description: str
    meta: dict


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def load_galaxies(galaxies_dir: Path) -> dict[str, Galaxy]:
    galaxies: dict[str, Galaxy] = {}
    for path in sorted(galaxies_dir.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        uuid = data.get("uuid")
        gtype = data.get("type")
        if not uuid or not gtype:
            continue
        galaxies[gtype] = Galaxy(
            uuid=uuid,
            type=gtype,
            name=data.get("name", gtype),
            description=data.get("description", ""),
        )
    return galaxies


def load_clusters(clusters_dir: Path) -> tuple[dict[str, Cluster], list[tuple[str, str, str]]]:
    clusters: dict[str, Cluster] = {}
    explicit_edges: list[tuple[str, str, str]] = []

    for path in sorted(clusters_dir.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)

        galaxy_type = data.get("type", "unknown")
        for index, raw_cluster in enumerate(data.get("values", []), start=1):
            uuid = raw_cluster.get("uuid") or f"{galaxy_type}:{index}"
            node_id = f"cluster:{uuid}"
            cluster = Cluster(
                node_id=node_id,
                uuid=uuid,
                value=raw_cluster.get("value", ""),
                galaxy_type=galaxy_type,
                description=raw_cluster.get("description", ""),
                meta=raw_cluster.get("meta", {}),
            )
            clusters[uuid] = cluster

            for relation in raw_cluster.get("related", []) or []:
                dest_uuid = relation.get("dest-uuid")
                relation_type = relation.get("type", "related-to")
                if dest_uuid:
                    explicit_edges.append((uuid, dest_uuid, relation_type))

    return clusters, explicit_edges


def cluster_terms(cluster: Cluster, include_synonyms: bool) -> set[str]:
    terms = set()
    if cluster.value:
        terms.add(normalize(cluster.value))

    if include_synonyms:
        synonyms = cluster.meta.get("synonyms", [])
        for synonym in synonyms:
            if isinstance(synonym, str) and synonym.strip():
                terms.add(normalize(synonym))

    return terms


def add_graphml_keys(root: ET.Element) -> None:
    keys = [
        ("d0", "node", "kind"),
        ("d1", "node", "uuid"),
        ("d2", "node", "name"),
        ("d3", "node", "galaxy_type"),
        ("d4", "node", "description"),
        ("d5", "edge", "relation_type"),
        ("d6", "edge", "relation_source"),
    ]
    for key_id, attr_for, attr_name in keys:
        ET.SubElement(
            root,
            "key",
            id=key_id,
            **{"for": attr_for, "attr.name": attr_name, "attr.type": "string"},
        )


def add_data(parent: ET.Element, key: str, value: str) -> None:
    data = ET.SubElement(parent, "data", key=key)
    data.text = value


def build_graphml(
    galaxies: dict[str, Galaxy],
    clusters: dict[str, Cluster],
    explicit_edges: list[tuple[str, str, str]],
    include_explicit_edges: bool,
    inferred_mode: str,
) -> ET.ElementTree:
    root = ET.Element("graphml", xmlns="http://graphml.graphdrawing.org/xmlns")
    add_graphml_keys(root)

    graph = ET.SubElement(root, "graph", id="misp_galaxies", edgedefault="directed")

    for galaxy in galaxies.values():
        node = ET.SubElement(graph, "node", id=f"galaxy:{galaxy.uuid}")
        add_data(node, "d0", "galaxy")
        add_data(node, "d1", galaxy.uuid)
        add_data(node, "d2", galaxy.name)
        add_data(node, "d3", galaxy.type)
        add_data(node, "d4", galaxy.description)

    for cluster in clusters.values():
        node = ET.SubElement(graph, "node", id=cluster.node_id)
        add_data(node, "d0", "cluster")
        add_data(node, "d1", cluster.uuid)
        add_data(node, "d2", cluster.value)
        add_data(node, "d3", cluster.galaxy_type)
        add_data(node, "d4", cluster.description)

        galaxy = galaxies.get(cluster.galaxy_type)
        if galaxy:
            edge = ET.SubElement(
                graph,
                "edge",
                source=f"galaxy:{galaxy.uuid}",
                target=cluster.node_id,
            )
            add_data(edge, "d5", "contains")
            add_data(edge, "d6", "membership")

    edge_counter = itertools.count(1)

    if include_explicit_edges:
        for source_uuid, target_uuid, relation_type in explicit_edges:
            source_cluster = clusters.get(source_uuid)
            target_cluster = clusters.get(target_uuid)
            if not source_cluster or not target_cluster:
                continue
            edge = ET.SubElement(
                graph,
                "edge",
                id=f"e{next(edge_counter)}",
                source=source_cluster.node_id,
                target=target_cluster.node_id,
            )
            add_data(edge, "d5", relation_type)
            add_data(edge, "d6", "explicit")

    if inferred_mode != "none":
        include_synonyms = inferred_mode == "value-or-synonyms"
        term_index: dict[str, list[Cluster]] = {}
        for cluster in clusters.values():
            for term in cluster_terms(cluster, include_synonyms=include_synonyms):
                term_index.setdefault(term, []).append(cluster)

        seen_pairs: set[tuple[str, str]] = set()
        for term, matching_clusters in term_index.items():
            if len(matching_clusters) < 2:
                continue

            for left, right in itertools.combinations(matching_clusters, 2):
                if left.galaxy_type == right.galaxy_type:
                    continue
                pair = tuple(sorted((left.uuid, right.uuid)))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)

                edge = ET.SubElement(
                    graph,
                    "edge",
                    id=f"e{next(edge_counter)}",
                    source=left.node_id,
                    target=right.node_id,
                )
                add_data(edge, "d5", "same-value")
                add_data(edge, "d6", f"inferred:{term}")

    return ET.ElementTree(root)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a GraphML graph from galaxies and clusters JSON files."
    )
    parser.add_argument(
        "--clusters-dir",
        type=Path,
        default=Path("clusters"),
        help="Directory containing cluster JSON files.",
    )
    parser.add_argument(
        "--galaxies-dir",
        type=Path,
        default=Path("galaxies"),
        help="Directory containing galaxy JSON files.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("misp-galaxies.graphml"),
        help="Output GraphML file path.",
    )
    parser.add_argument(
        "--no-existing-relationships",
        action="store_true",
        help="Disable explicit relationships from cluster related[] entries.",
    )
    parser.add_argument(
        "--cross-cluster-matching",
        choices=["none", "value", "value-or-synonyms"],
        default="none",
        help=(
            "Create inferred edges across different galaxy types by matching cluster values "
            "or values+synonyms."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    galaxies = load_galaxies(args.galaxies_dir)
    clusters, explicit_edges = load_clusters(args.clusters_dir)

    graphml = build_graphml(
        galaxies=galaxies,
        clusters=clusters,
        explicit_edges=explicit_edges,
        include_explicit_edges=not args.no_existing_relationships,
        inferred_mode=args.cross_cluster_matching,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    graphml.write(args.output, encoding="utf-8", xml_declaration=True)

    print(
        f"GraphML written to {args.output} with {len(galaxies)} galaxies and {len(clusters)} clusters."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
