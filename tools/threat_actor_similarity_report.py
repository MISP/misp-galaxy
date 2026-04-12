#!/usr/bin/env python3
# coding=utf-8
"""Generate a similarity report for potential duplicate/similar threat actors."""

import argparse
import itertools
import json
import re
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path


def normalize_name(value: str) -> str:
    """Normalize actor/alias names for comparison."""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def load_threat_actor_names(cluster_path: Path):
    """Return a map: normalized name -> set of canonical threat actor names."""
    data = json.loads(cluster_path.read_text(encoding="utf-8"))
    names_to_actors = {}

    for entry in data.get("values", []):
        canonical_name = entry.get("value", "").strip()
        if not canonical_name:
            continue

        all_names = [canonical_name]
        meta = entry.get("meta") or {}
        synonyms = meta.get("synonyms") or []
        if isinstance(synonyms, list):
            all_names.extend([s for s in synonyms if isinstance(s, str)])

        for raw_name in all_names:
            normalized = normalize_name(raw_name)
            if not normalized:
                continue
            names_to_actors.setdefault(normalized, set()).add(canonical_name)

    return names_to_actors


def find_similar_name_pairs(names_to_actors, min_similarity=0.88, max_results=200):
    """Compute similar name pairs using difflib.SequenceMatcher."""
    names = sorted(names_to_actors)
    results = []

    # A cheap pre-filter: similarity cannot pass threshold if string lengths differ too much.
    max_len_ratio_delta = (1.0 - min_similarity) / max(min_similarity, 1e-9)

    for left, right in itertools.combinations(names, 2):
        # Skip identical forms and aliases of exactly the same actor only.
        if left == right:
            continue

        left_actors = names_to_actors[left]
        right_actors = names_to_actors[right]
        if left_actors == right_actors:
            continue

        longer = max(len(left), len(right))
        shorter = min(len(left), len(right))
        if shorter == 0:
            continue
        if (longer - shorter) / shorter > max_len_ratio_delta:
            continue

        matcher = SequenceMatcher(None, left, right)
        if matcher.quick_ratio() < min_similarity:
            continue
        score = matcher.ratio()
        if score < min_similarity:
            continue

        results.append(
            {
                "score": round(score, 4),
                "name_1": left,
                "actors_1": sorted(left_actors),
                "name_2": right,
                "actors_2": sorted(right_actors),
            }
        )

    results.sort(key=lambda item: (-item["score"], item["name_1"], item["name_2"]))
    return results[:max_results]


def build_markdown_report(results, source_path: Path, min_similarity: float, max_results: int):
    """Build a markdown report containing potential similar threat-actor names."""
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Threat-Actor Similarity Report",
        "",
        f"- Generated: {generated_at}",
        f"- Source cluster: `{source_path}`",
        f"- Similarity method: `difflib.SequenceMatcher.ratio()`",
        f"- Threshold: `{min_similarity}`",
        f"- Max results: `{max_results}`",
        f"- Matches returned: `{len(results)}`",
        "",
    ]

    if not results:
        lines.append("No potential similar names found with current threshold.")
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            "| score | name_1 | actor(s)_1 | name_2 | actor(s)_2 |",
            "|---:|---|---|---|---|",
        ]
    )
    for item in results:
        lines.append(
            "| {score:.4f} | `{name_1}` | {actors_1} | `{name_2}` | {actors_2} |".format(
                score=item["score"],
                name_1=item["name_1"],
                actors_1=", ".join(item["actors_1"]),
                name_2=item["name_2"],
                actors_2=", ".join(item["actors_2"]),
            )
        )

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Find potential similar threat-actor names and aliases in a MISP galaxy "
            "cluster using SequenceMatcher."
        )
    )
    parser.add_argument(
        "--cluster",
        default="clusters/threat-actor.json",
        help="Path to the cluster JSON file (default: clusters/threat-actor.json)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.88,
        help="Minimum similarity ratio [0.0-1.0] (default: 0.88)",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=200,
        help="Maximum number of similar pairs to report (default: 200)",
    )
    parser.add_argument(
        "--markdown-output",
        default="threat_actor_similarity_report.md",
        help="Path for markdown report output (default: threat_actor_similarity_report.md)",
    )
    parser.add_argument(
        "--json-output",
        default="",
        help="Optional path for JSON output",
    )
    args = parser.parse_args()

    if not 0.0 <= args.threshold <= 1.0:
        raise ValueError("--threshold must be in [0.0, 1.0]")

    cluster_path = Path(args.cluster)
    names_to_actors = load_threat_actor_names(cluster_path)
    results = find_similar_name_pairs(
        names_to_actors,
        min_similarity=args.threshold,
        max_results=args.max_results,
    )

    markdown = build_markdown_report(
        results,
        source_path=cluster_path,
        min_similarity=args.threshold,
        max_results=args.max_results,
    )
    output_path = Path(args.markdown_output)
    output_path.write_text(markdown, encoding="utf-8")

    if args.json_output:
        json_path = Path(args.json_output)
        json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Analyzed normalized names: {len(names_to_actors)}")
    print(f"Potential similar name pairs: {len(results)}")
    print(f"Markdown report written to: {output_path}")
    if args.json_output:
        print(f"JSON report written to: {args.json_output}")


if __name__ == "__main__":
    main()
