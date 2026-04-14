#!/usr/bin/env python3
"""Generate graph exports for MISP galaxies and clusters.

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


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    kind: str
    uuid: str
    name: str
    galaxy_type: str
    description: str


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    relation_type: str
    relation_source: str
    edge_id: str | None = None


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def parse_name_filters(raw_values: list[str]) -> set[str]:
    filters: set[str] = set()
    for raw_value in raw_values:
        for value in raw_value.split(","):
            normalized = normalize(value)
            if normalized:
                filters.add(normalized)
    return filters


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


def build_graph(
    galaxies: dict[str, Galaxy],
    clusters: dict[str, Cluster],
    explicit_edges: list[tuple[str, str, str]],
    include_explicit_edges: bool,
    inferred_mode: str,
) -> tuple[list[GraphNode], list[GraphEdge]]:
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    for galaxy in galaxies.values():
        nodes.append(
            GraphNode(
                node_id=f"galaxy:{galaxy.uuid}",
                kind="galaxy",
                uuid=galaxy.uuid,
                name=galaxy.name,
                galaxy_type=galaxy.type,
                description=galaxy.description,
            )
        )

    for cluster in clusters.values():
        nodes.append(
            GraphNode(
                node_id=cluster.node_id,
                kind="cluster",
                uuid=cluster.uuid,
                name=cluster.value,
                galaxy_type=cluster.galaxy_type,
                description=cluster.description,
            )
        )

        galaxy = galaxies.get(cluster.galaxy_type)
        if galaxy:
            edges.append(
                GraphEdge(
                    source=f"galaxy:{galaxy.uuid}",
                    target=cluster.node_id,
                    relation_type="contains",
                    relation_source="membership",
                )
            )

    edge_counter = itertools.count(1)

    if include_explicit_edges:
        for source_uuid, target_uuid, relation_type in explicit_edges:
            source_cluster = clusters.get(source_uuid)
            target_cluster = clusters.get(target_uuid)
            if not source_cluster or not target_cluster:
                continue
            edges.append(
                GraphEdge(
                    edge_id=f"e{next(edge_counter)}",
                    source=source_cluster.node_id,
                    target=target_cluster.node_id,
                    relation_type=relation_type,
                    relation_source="explicit",
                )
            )

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

                edges.append(
                    GraphEdge(
                        edge_id=f"e{next(edge_counter)}",
                        source=left.node_id,
                        target=right.node_id,
                        relation_type="same-value",
                        relation_source=f"inferred:{term}",
                    )
                )

    return nodes, edges


def build_graphml(nodes: list[GraphNode], edges: list[GraphEdge]) -> ET.ElementTree:
    root = ET.Element("graphml", xmlns="http://graphml.graphdrawing.org/xmlns")
    add_graphml_keys(root)
    graph = ET.SubElement(root, "graph", id="misp_galaxies", edgedefault="directed")

    for graph_node in nodes:
        node = ET.SubElement(graph, "node", id=graph_node.node_id)
        add_data(node, "d0", graph_node.kind)
        add_data(node, "d1", graph_node.uuid)
        add_data(node, "d2", graph_node.name)
        add_data(node, "d3", graph_node.galaxy_type)
        add_data(node, "d4", graph_node.description)

    for graph_edge in edges:
        edge_kwargs = {"source": graph_edge.source, "target": graph_edge.target}
        if graph_edge.edge_id:
            edge_kwargs["id"] = graph_edge.edge_id
        edge = ET.SubElement(graph, "edge", **edge_kwargs)
        add_data(edge, "d5", graph_edge.relation_type)
        add_data(edge, "d6", graph_edge.relation_source)

    return ET.ElementTree(root)


def to_dot(nodes: list[GraphNode], edges: list[GraphEdge]) -> str:
    lines = ["digraph misp_galaxies {"]
    for graph_node in nodes:
        label = graph_node.name.replace('"', '\\"')
        lines.append(f'  "{graph_node.node_id}" [label="{label}", kind="{graph_node.kind}"];')
    for graph_edge in edges:
        lines.append(
            f'  "{graph_edge.source}" -> "{graph_edge.target}" [label="{graph_edge.relation_type}"];'
        )
    lines.append("}")
    return "\n".join(lines) + "\n"


def to_json_graph(nodes: list[GraphNode], edges: list[GraphEdge]) -> str:
    payload = {
        "nodes": [
            {
                "id": graph_node.node_id,
                "kind": graph_node.kind,
                "uuid": graph_node.uuid,
                "name": graph_node.name,
                "galaxy_type": graph_node.galaxy_type,
                "description": graph_node.description,
            }
            for graph_node in nodes
        ],
        "edges": [
            {
                "id": graph_edge.edge_id,
                "source": graph_edge.source,
                "target": graph_edge.target,
                "relation_type": graph_edge.relation_type,
                "relation_source": graph_edge.relation_source,
            }
            for graph_edge in edges
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def output_suffix(output_format: str) -> str:
    """Return the expected file suffix for each supported output format."""
    return {
        "graphml": ".graphml",
        "dot": ".dot",
        "json-graph": ".json",
    }[output_format]


def resolve_output_path(requested_path: Path, output_format: str) -> Path:
    """Ensure output file extension matches the selected graph export format."""
    expected_suffix = output_suffix(output_format)
    if requested_path.suffix != expected_suffix:
        return requested_path.with_suffix(expected_suffix)
    return requested_path


def filter_graph_data(
    galaxies: dict[str, Galaxy],
    clusters: dict[str, Cluster],
    selected_galaxy_names: set[str],
    selected_cluster_names: set[str],
) -> tuple[dict[str, Galaxy], dict[str, Cluster]]:
    filtered_galaxy_types: set[str] | None = None
    if selected_galaxy_names:
        filtered_galaxy_types = {
            galaxy.type
            for galaxy in galaxies.values()
            if normalize(galaxy.name) in selected_galaxy_names
            or normalize(galaxy.type) in selected_galaxy_names
        }

    filtered_clusters = {
        uuid: cluster
        for uuid, cluster in clusters.items()
        if (
            filtered_galaxy_types is None or cluster.galaxy_type in filtered_galaxy_types
        )
        and (
            not selected_cluster_names
            or normalize(cluster.value) in selected_cluster_names
        )
    }

    if filtered_galaxy_types is None:
        filtered_galaxy_types = {cluster.galaxy_type for cluster in filtered_clusters.values()}

    filtered_galaxies = {
        gtype: galaxy
        for gtype, galaxy in galaxies.items()
        if gtype in filtered_galaxy_types
    }
    return filtered_galaxies, filtered_clusters


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a graph export from MISP galaxy and cluster JSON files "
            "(GraphML, Graphviz DOT, or JSON graph)."
        )
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
        help="Output file path (its extension is aligned with --output-format).",
    )
    parser.add_argument(
        "--output-format",
        choices=["graphml", "dot", "json-graph"],
        default="graphml",
        help="Output format: GraphML (default), Graphviz DOT, or JSON graph.",
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
    parser.add_argument(
        "--select-galaxy-name",
        action="append",
        default=[],
        metavar="NAME",
        help=(
            "Limit export to matching galaxy names or types. Repeat or pass a comma-separated "
            "list (case-insensitive)."
        ),
    )
    parser.add_argument(
        "--select-cluster-name",
        action="append",
        default=[],
        metavar="NAME",
        help=(
            "Limit export to matching cluster values. Repeat or pass a comma-separated list "
            "(case-insensitive)."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    galaxies = load_galaxies(args.galaxies_dir)
    clusters, explicit_edges = load_clusters(args.clusters_dir)
    selected_galaxy_names = parse_name_filters(args.select_galaxy_name)
    selected_cluster_names = parse_name_filters(args.select_cluster_name)
    galaxies, clusters = filter_graph_data(
        galaxies=galaxies,
        clusters=clusters,
        selected_galaxy_names=selected_galaxy_names,
        selected_cluster_names=selected_cluster_names,
    )

    nodes, edges = build_graph(
        galaxies=galaxies,
        clusters=clusters,
        explicit_edges=explicit_edges,
        include_explicit_edges=not args.no_existing_relationships,
        inferred_mode=args.cross_cluster_matching,
    )

    output_path = resolve_output_path(args.output, args.output_format)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.output_format == "graphml":
        graphml = build_graphml(nodes, edges)
        graphml.write(output_path, encoding="utf-8", xml_declaration=True)
    elif args.output_format == "dot":
        output_path.write_text(to_dot(nodes, edges), encoding="utf-8")
    else:
        output_path.write_text(to_json_graph(nodes, edges), encoding="utf-8")

    print(
        f"{args.output_format} graph written to {output_path} with {len(galaxies)} galaxies and {len(clusters)} clusters."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
