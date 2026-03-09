#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate a MISP galaxy + cluster from the Government of Canada listed terrorist
entities XML feed.

Source XML (default):
https://www.publicsafety.gc.ca/cnt/_xml/lstd-ntts-eng.xml
"""

import argparse
import json
import re
import uuid
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

import requests

SOURCE_URL = "https://www.publicsafety.gc.ca/cnt/_xml/lstd-ntts-eng.xml"
UUID_NS = uuid.UUID("ec8b707d-c675-40f8-9f31-9b6316f8fba8")


def strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def clean_key(tag: str) -> str:
    tag = strip_ns(tag)
    return re.sub(r"[^a-z0-9]+", "_", tag.lower()).strip("_")


def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def find_record_elements(root: ET.Element) -> List[ET.Element]:
    signatures = Counter()
    by_tag: Dict[str, List[ET.Element]] = {}

    for element in root.iter():
        children = [c for c in element if isinstance(c.tag, str)]
        if len(children) < 2:
            continue
        child_tags = tuple(sorted(clean_key(c.tag) for c in children))
        if len(set(child_tags)) < 2:
            continue
        record_tag = clean_key(element.tag)
        signatures[(record_tag, child_tags)] += 1
        by_tag.setdefault(record_tag, []).append(element)

    if not signatures:
        raise ValueError("Unable to identify repeating record elements in XML.")

    (record_tag, _), _ = signatures.most_common(1)[0]
    return by_tag[record_tag]


def parse_record(record: ET.Element) -> Dict[str, str]:
    parsed: Dict[str, str] = {}

    for child in record:
        key = clean_key(child.tag)
        value = clean_text("".join(child.itertext()))
        if not value:
            continue
        if key in parsed:
            parsed[key] = f"{parsed[key]} | {value}"
        else:
            parsed[key] = value

    return parsed


def select_value(fields: Dict[str, str], index: int) -> str:
    preferred = [
        "name",
        "entity_name",
        "listed_entity",
        "organisation",
        "organization",
        "group_name",
        "title",
    ]
    for key in preferred:
        if fields.get(key):
            return fields[key]

    for key, value in fields.items():
        if "name" in key and value:
            return value

    return f"Unnamed entity #{index}"


def extract_aliases(fields: Dict[str, str]) -> List[str]:
    aliases = []
    for key, value in fields.items():
        if any(k in key for k in ["alias", "aka", "also_known", "also_known_as"]):
            split_values = re.split(r"\s*[;|/,]\s*", value)
            aliases.extend(v for v in split_values if v)
    # keep order, remove dupes
    return list(dict.fromkeys(aliases))


def extract_refs(fields: Dict[str, str]) -> List[str]:
    refs = []
    for value in fields.values():
        refs.extend(re.findall(r"https?://[^\s,]+", value))
    return list(dict.fromkeys(refs))


def build_cluster(values: List[Dict[str, object]]) -> Dict[str, object]:
    return {
        "authors": ["Public Safety Canada", "MISP Project"],
        "category": "threat-actor",
        "description": "Entities listed under Canada's Criminal Code as terrorist entities.",
        "name": "Canada Listed Terrorist Entities",
        "source": SOURCE_URL,
        "type": "canada-listed-terrorist-entities",
        "uuid": "7c650f6f-e2bb-4af1-aaf0-bf57a2bd7e87",
        "values": values,
        "version": 1,
    }


def build_galaxy() -> Dict[str, object]:
    return {
        "description": "Entities listed under Canada's Criminal Code as terrorist entities.",
        "icon": "user-secret",
        "name": "Canada Listed Terrorist Entities",
        "namespace": "ca",
        "type": "canada-listed-terrorist-entities",
        "uuid": "14804140-18e2-478e-a608-f9929006cc4f",
        "version": 1,
    }


def read_xml(xml_file: Optional[str], xml_url: str) -> str:
    if xml_file:
        return Path(xml_file).read_text(encoding="utf-8")

    response = requests.get(xml_url, timeout=30)
    response.raise_for_status()
    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MISP galaxy/cluster from Canada listed terrorist entities XML")
    parser.add_argument("--xml-file", help="Path to local XML file (alternative to --xml-url)")
    parser.add_argument("--xml-url", default=SOURCE_URL, help="Remote XML URL")
    parser.add_argument("--cluster-output", default="../clusters/canada-listed-terrorist-entities.json")
    parser.add_argument("--galaxy-output", default="../galaxies/canada-listed-terrorist-entities.json")
    args = parser.parse_args()

    xml_text = read_xml(args.xml_file, args.xml_url)
    root = ET.fromstring(xml_text)

    records = find_record_elements(root)
    values = []
    for idx, record in enumerate(records, start=1):
        fields = parse_record(record)
        if not fields:
            continue

        value = select_value(fields, idx)
        aliases = extract_aliases(fields)
        refs = extract_refs(fields)

        description_parts = []
        for key, field_value in fields.items():
            if field_value == value:
                continue
            pretty_key = key.replace("_", " ").title()
            description_parts.append(f"{pretty_key}: {field_value}")
        description = "\n".join(description_parts) if description_parts else value

        cluster = {
            "value": value,
            "description": description,
            "uuid": str(uuid.uuid5(UUID_NS, value)),
            "meta": {"raw_fields": fields},
        }
        if aliases:
            cluster["meta"]["synonyms"] = aliases
        if refs:
            cluster["meta"]["refs"] = refs

        values.append(cluster)

    values.sort(key=lambda item: item["value"].lower())

    galaxy = build_galaxy()
    cluster = build_cluster(values)

    Path(args.galaxy_output).write_text(json.dumps(galaxy, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.cluster_output).write_text(json.dumps(cluster, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Generated {len(values)} clusters")
    print(f"Galaxy file : {args.galaxy_output}")
    print(f"Cluster file: {args.cluster_output}")


if __name__ == "__main__":
    main()
