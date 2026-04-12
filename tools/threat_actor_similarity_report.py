#!/usr/bin/env python3
# coding=utf-8
"""Generate a similarity report for potential duplicate/similar threat actors."""

import argparse
import itertools
import json
import math
import re
import zlib
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path


ALGORITHMS = ("sequence", "levenshtein", "compression", "vector")


def normalize_name(value: str) -> str:
    """Normalize actor/alias names for comparison."""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def strip_numeric_tokens(value: str) -> str:
    """Return a normalized name with digits removed (keeps non-numeric tokens)."""
    value = re.sub(r"\d+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def numeric_tokens(value: str):
    """Extract numeric token sequences from a normalized name."""
    return tuple(re.findall(r"\d+", value))


def load_threat_actor_names(cluster_path: Path):
    """Return a map: normalized name -> map of canonical threat actor name -> UUID."""
    data = json.loads(cluster_path.read_text(encoding="utf-8"))
    names_to_actors = {}

    for entry in data.get("values", []):
        canonical_name = entry.get("value", "").strip()
        canonical_uuid = entry.get("uuid", "").strip()
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
            actors_for_name = names_to_actors.setdefault(normalized, {})
            actors_for_name[canonical_name] = canonical_uuid

    return names_to_actors


def should_compare_pair(left: str, right: str, min_similarity: float) -> bool:
    """Fast filters to skip noisy/clearly impossible candidates."""
    if left == right:
        return False

    left_non_numeric = strip_numeric_tokens(left)
    right_non_numeric = strip_numeric_tokens(right)
    left_numbers = numeric_tokens(left)
    right_numbers = numeric_tokens(right)

    # Threat-actor names often reuse a textual stem with a different numeric id.
    # Treat these as distinct identifiers to avoid over-reporting false positives.
    if (
        left_numbers
        and right_numbers
        and left_non_numeric
        and right_non_numeric
        and left_non_numeric == right_non_numeric
        and left_numbers != right_numbers
    ):
        return False

    # A cheap pre-filter: similarity cannot pass threshold if string lengths differ too much.
    max_len_ratio_delta = (1.0 - min_similarity) / max(min_similarity, 1e-9)
    longer = max(len(left), len(right))
    shorter = min(len(left), len(right))
    if shorter == 0:
        return False
    if (longer - shorter) / shorter > max_len_ratio_delta:
        return False

    return True


def sequence_similarity(left: str, right: str) -> float:
    """difflib.SequenceMatcher ratio."""
    matcher = SequenceMatcher(None, left, right)
    return matcher.ratio()


def levenshtein_similarity(left: str, right: str) -> float:
    """Normalized Levenshtein similarity: 1 - distance / max_len."""
    if left == right:
        return 1.0
    if not left or not right:
        return 0.0

    if len(left) < len(right):
        left, right = right, left

    previous_row = list(range(len(right) + 1))
    for i, left_ch in enumerate(left, start=1):
        current_row = [i]
        for j, right_ch in enumerate(right, start=1):
            insertions = previous_row[j] + 1
            deletions = current_row[j - 1] + 1
            substitutions = previous_row[j - 1] + (left_ch != right_ch)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    distance = previous_row[-1]
    return 1.0 - (distance / max(len(left), len(right)))


def compression_similarity(left: str, right: str) -> float:
    """Compression-based similarity derived from Normalized Compression Distance."""

    def clen(text: str) -> int:
        return len(zlib.compress(text.encode("utf-8")))

    c_left = clen(left)
    c_right = clen(right)
    c_joined = clen(f"{left}|{right}")
    ncd = (c_joined - min(c_left, c_right)) / max(c_left, c_right)
    return max(0.0, min(1.0, 1.0 - ncd))


def char_ngram_counter(text: str, n: int = 3) -> Counter:
    """Character n-gram bag for vector comparison."""
    padded = f" {text} "
    if len(padded) < n:
        return Counter({padded: 1})
    return Counter(padded[i : i + n] for i in range(len(padded) - n + 1))


def vector_similarity(left: str, right: str) -> float:
    """Cosine similarity over character n-gram count vectors."""
    vec_left = char_ngram_counter(left)
    vec_right = char_ngram_counter(right)

    common_keys = set(vec_left) & set(vec_right)
    numerator = sum(vec_left[k] * vec_right[k] for k in common_keys)
    if numerator == 0:
        return 0.0

    norm_left = math.sqrt(sum(v * v for v in vec_left.values()))
    norm_right = math.sqrt(sum(v * v for v in vec_right.values()))
    if not norm_left or not norm_right:
        return 0.0

    return numerator / (norm_left * norm_right)


def get_similarity(algorithm: str, left: str, right: str) -> float:
    """Dispatch algorithm scorer."""
    if algorithm == "sequence":
        return sequence_similarity(left, right)
    if algorithm == "levenshtein":
        return levenshtein_similarity(left, right)
    if algorithm == "compression":
        return compression_similarity(left, right)
    if algorithm == "vector":
        return vector_similarity(left, right)
    raise ValueError(f"Unknown algorithm: {algorithm}")


def find_similar_name_pairs(
    names_to_actors,
    algorithms,
    min_similarity=0.88,
    max_results=200,
    combine_mode="union",
):
    """Compute similar name pairs using one or more similarity algorithms."""
    names = sorted(names_to_actors)
    results = []

    for left, right in itertools.combinations(names, 2):
        left_actors = names_to_actors[left]
        right_actors = names_to_actors[right]
        if left_actors == right_actors:
            continue
        if not should_compare_pair(left, right, min_similarity):
            continue

        algorithm_scores = {}
        for algorithm in algorithms:
            score = get_similarity(algorithm, left, right)
            if score >= min_similarity:
                algorithm_scores[algorithm] = round(score, 4)

        if combine_mode == "intersection":
            include = len(algorithm_scores) == len(algorithms)
        else:
            include = bool(algorithm_scores)

        if not include:
            continue

        aggregate_score = sum(algorithm_scores.values()) / len(algorithm_scores)
        results.append(
            {
                "score": round(aggregate_score, 4),
                "algorithm_scores": algorithm_scores,
                "name_1": left,
                "actors_1": sorted(left_actors.items()),
                "name_2": right,
                "actors_2": sorted(right_actors.items()),
            }
        )

    results.sort(key=lambda item: (-item["score"], item["name_1"], item["name_2"]))
    return results[:max_results]


def build_markdown_report(
    results,
    source_path: Path,
    min_similarity: float,
    max_results: int,
    algorithms,
    combine_mode,
):
    """Build a markdown report containing potential similar threat-actor names."""
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    def format_actors(actors):
        return ", ".join(f"`{name}` ({uuid or 'N/A'})" for name, uuid in actors)

    lines = [
        "# Threat-Actor Similarity Report",
        "",
        f"- Generated: {generated_at}",
        f"- Source cluster: `{source_path}`",
        f"- Similarity algorithms: `{', '.join(algorithms)}`",
        f"- Combine mode: `{combine_mode}`",
        f"- Threshold: `{min_similarity}`",
        f"- Max results: `{max_results}`",
        f"- Matches returned: `{len(results)}`",
        "",
    ]

    if not results:
        lines.append("No potential similar names found with current threshold/settings.")
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            "| score | algorithm_scores | name_1 | actor(s)_1 | name_2 | actor(s)_2 |",
            "|---:|---|---|---|---|---|",
        ]
    )
    for item in results:
        score_parts = ", ".join(f"{k}:{v:.4f}" for k, v in sorted(item["algorithm_scores"].items()))
        lines.append(
            "| {score:.4f} | `{scores}` | `{name_1}` | {actors_1} | `{name_2}` | {actors_2} |".format(
                score=item["score"],
                scores=score_parts,
                name_1=item["name_1"],
                actors_1=format_actors(item["actors_1"]),
                name_2=item["name_2"],
                actors_2=format_actors(item["actors_2"]),
            )
        )

    return "\n".join(lines) + "\n"


def parse_algorithms(value: str):
    """Parse comma-separated algorithms; special keyword: all."""
    raw = [part.strip().lower() for part in value.split(",") if part.strip()]
    if not raw:
        raise ValueError("--algorithms cannot be empty")
    if "all" in raw:
        return list(ALGORITHMS)

    invalid = [name for name in raw if name not in ALGORITHMS]
    if invalid:
        allowed = ", ".join(ALGORITHMS) + ", all"
        raise ValueError(f"Unknown algorithm(s): {', '.join(invalid)}. Allowed: {allowed}")

    # Preserve user order while removing duplicates.
    return list(dict.fromkeys(raw))


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Find potential similar threat-actor names and aliases in a MISP galaxy "
            "cluster using configurable similarity algorithms."
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
        "--algorithms",
        default="sequence",
        help=(
            "Comma-separated algorithms to use: sequence, levenshtein, compression, "
            "vector, or all (default: sequence)"
        ),
    )
    parser.add_argument(
        "--combine-mode",
        choices=("union", "intersection"),
        default="union",
        help=(
            "How to combine multi-algorithm results: union (any algorithm passes) or "
            "intersection (all selected algorithms must pass). Default: union"
        ),
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

    algorithms = parse_algorithms(args.algorithms)

    cluster_path = Path(args.cluster)
    names_to_actors = load_threat_actor_names(cluster_path)
    results = find_similar_name_pairs(
        names_to_actors,
        algorithms=algorithms,
        min_similarity=args.threshold,
        max_results=args.max_results,
        combine_mode=args.combine_mode,
    )

    markdown = build_markdown_report(
        results,
        source_path=cluster_path,
        min_similarity=args.threshold,
        max_results=args.max_results,
        algorithms=algorithms,
        combine_mode=args.combine_mode,
    )
    output_path = Path(args.markdown_output)
    output_path.write_text(markdown, encoding="utf-8")

    if args.json_output:
        json_path = Path(args.json_output)
        json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Analyzed normalized names: {len(names_to_actors)}")
    print(f"Potential similar name pairs: {len(results)}")
    print(f"Algorithms: {', '.join(algorithms)}")
    print(f"Combine mode: {args.combine_mode}")
    print(f"Markdown report written to: {output_path}")
    if args.json_output:
        print(f"JSON report written to: {args.json_output}")


if __name__ == "__main__":
    main()
