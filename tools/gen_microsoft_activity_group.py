#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Update the Microsoft Activity Group cluster from Microsoft's public mapping feed.

The tool is designed to preserve existing curated content (notably existing
relationships and descriptions), while enriching entries with new names,
synonyms, references and optional cross-links to the threat-actor cluster.
"""

from __future__ import annotations

import argparse
import json
import re
import uuid
from pathlib import Path
from typing import Any
from urllib.request import urlopen


MICROSOFT_MAPPING_URL = (
    "https://raw.githubusercontent.com/microsoft/mstic/master/"
    "PublicFeeds/ThreatActorNaming/MicrosoftMapping.json"
)
DEFAULT_OUTPUT = Path("clusters/microsoft-activity-group.json")
DEFAULT_INPUT = Path("clusters/microsoft-activity-group.json")
THREAT_ACTOR_CLUSTER = Path("clusters/threat-actor.json")
REL_PROBABLE = 'estimative-language:likelihood-probability="likely"'
UUID_NAMESPACE = uuid.UUID("28b5e55d-acba-4748-a79d-0afa3512689a")


COUNTRY_CODES = {
    "austria": "AT",
    "belarus": "BY",
    "china": "CN",
    "iran": "IR",
    "israel": "IL",
    "lebanon": "LB",
    "north korea": "KP",
    "pakistan": "PK",
    "russia": "RU",
    "singapore": "SG",
    "turkiye": "TR",
    "türkiye": "TR",
    "ukraine": "UA",
    "united arab emirates": "AE",
    "vietnam": "VN",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Update clusters/microsoft-activity-group.json from Microsoft's "
            "ThreatActorNaming mapping feed."
        )
    )
    parser.add_argument(
        "--url",
        default=MICROSOFT_MAPPING_URL,
        help="JSON feed URL (default: Microsoft public feed)",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Existing microsoft-activity-group cluster to read",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path where the updated cluster will be written",
    )
    parser.add_argument(
        "--threat-actor",
        type=Path,
        default=THREAT_ACTOR_CLUSTER,
        help="Path to threat-actor cluster used for relationship linking",
    )
    parser.add_argument(
        "--link-threat-actors",
        action="store_true",
        help=(
            "Add/maintain 'similar' relationships to entries in "
            "clusters/threat-actor.json when names or synonyms match"
        ),
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output with indentation",
    )
    return parser.parse_args()


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def split_aliases(alias_blob: str) -> list[str]:
    if not alias_blob:
        return []
    out: list[str] = []
    for raw_alias in alias_blob.split(","):
        alias = raw_alias.strip()
        if alias:
            out.append(alias)
    return out


def unique_list(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in values:
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def fetch_mapping(url: str) -> list[dict[str, str]]:
    with urlopen(url) as response:  # nosec B310 - URL is user-controlled by design
        payload = json.load(response)
    if not isinstance(payload, list):
        raise ValueError("Expected a list at Microsoft mapping endpoint")
    return payload


def build_threat_actor_index(cluster: dict[str, Any]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for actor in cluster.get("values", []):
        actor_uuid = actor.get("uuid")
        if not actor_uuid:
            continue
        candidates = [actor.get("value", "")]
        candidates.extend(actor.get("meta", {}).get("synonyms", []))
        for candidate in candidates:
            if not candidate:
                continue
            normalized = normalize_name(candidate)
            index.setdefault(normalized, set()).add(actor_uuid)
    return index


def extract_country_code(origin_threat: str) -> str | None:
    if not origin_threat:
        return None
    first_token = origin_threat.split(",", 1)[0].strip().casefold()
    return COUNTRY_CODES.get(first_token)


def create_entry(record: dict[str, str], source_url: str) -> dict[str, Any]:
    value = record["Threat actor name"].strip()
    origin = record.get("Origin/Threat", "").strip()
    aliases = split_aliases(record.get("Other names", ""))

    description = "Microsoft threat actor profile from the public naming mapping feed."
    if origin:
        description = f"Microsoft threat actor profile. Origin/Threat: {origin}."

    entry: dict[str, Any] = {
        "value": value,
        "description": description,
        "uuid": str(uuid.uuid5(UUID_NAMESPACE, value.casefold())),
        "meta": {
            "refs": [source_url],
            "synonyms": aliases,
            "microsoft-origin-threat": origin,
        },
    }

    country_code = extract_country_code(origin)
    if country_code:
        entry["meta"]["country"] = country_code

    if not aliases:
        entry["meta"].pop("synonyms")

    if not origin:
        entry["meta"].pop("microsoft-origin-threat")

    return entry


def merge_entry(existing: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    merged.setdefault("value", candidate["value"])
    merged.setdefault("uuid", candidate["uuid"])

    # Keep curated descriptions; only fill when missing.
    if not merged.get("description") and candidate.get("description"):
        merged["description"] = candidate["description"]

    meta = dict(merged.get("meta", {}))
    cand_meta = candidate.get("meta", {})

    refs = meta.get("refs", []) + cand_meta.get("refs", [])
    if refs:
        meta["refs"] = unique_list(refs)

    synonyms = meta.get("synonyms", []) + cand_meta.get("synonyms", [])
    if synonyms:
        meta["synonyms"] = unique_list(synonyms)

    if "microsoft-origin-threat" in cand_meta:
        meta["microsoft-origin-threat"] = cand_meta["microsoft-origin-threat"]

    if "country" not in meta and "country" in cand_meta:
        meta["country"] = cand_meta["country"]

    merged["meta"] = meta
    return merged


def add_threat_actor_relationships(
    entry: dict[str, Any],
    threat_actor_index: dict[str, set[str]],
) -> None:
    related = list(entry.get("related", []))
    existing_dest = {item.get("dest-uuid") for item in related if item.get("dest-uuid")}

    candidates = [entry.get("value", "")]
    candidates.extend(entry.get("meta", {}).get("synonyms", []))

    matched: set[str] = set()
    for candidate in candidates:
        normalized = normalize_name(candidate)
        matched.update(threat_actor_index.get(normalized, set()))

    for actor_uuid in sorted(matched):
        if actor_uuid in existing_dest:
            continue
        related.append({"dest-uuid": actor_uuid, "type": "similar", "tags": [REL_PROBABLE]})

    if related:
        entry["related"] = related


def main() -> None:
    args = parse_args()

    microsoft_cluster = load_json(args.input)
    mapping_records = fetch_mapping(args.url)

    threat_actor_index: dict[str, set[str]] = {}
    if args.link_threat_actors:
        threat_actor_cluster = load_json(args.threat_actor)
        threat_actor_index = build_threat_actor_index(threat_actor_cluster)

    existing_values = microsoft_cluster.get("values", [])
    by_name = {item.get("value", ""): item for item in existing_values}

    created = 0
    updated = 0

    for record in mapping_records:
        if "Threat actor name" not in record:
            continue
        candidate = create_entry(record, args.url)
        actor_name = candidate["value"]

        if actor_name in by_name:
            merged = merge_entry(by_name[actor_name], candidate)
            by_name[actor_name] = merged
            updated += 1
        else:
            by_name[actor_name] = candidate
            created += 1

    final_values = list(by_name.values())

    if args.link_threat_actors:
        for entry in final_values:
            add_threat_actor_relationships(entry, threat_actor_index)

    microsoft_cluster["values"] = sorted(final_values, key=lambda item: item.get("value", "").casefold())

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as fh:
        if args.pretty:
            json.dump(microsoft_cluster, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        else:
            json.dump(microsoft_cluster, fh, ensure_ascii=False, sort_keys=True)
            fh.write("\n")

    print(
        f"Done. Processed {len(mapping_records)} Microsoft records. "
        f"Updated {updated}, created {created}."
    )


if __name__ == "__main__":
    main()
