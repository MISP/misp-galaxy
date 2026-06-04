#!/usr/bin/env python3
"""Generate the PLOT4ai MISP galaxy from the upstream PLOT4ai deck JSON.

The source deck is maintained at:
https://github.com/PLOT4ai/plot4ai-library/blob/main/deck.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib.request import urlopen

RAW_DECK_URL = "https://raw.githubusercontent.com/PLOT4ai/plot4ai-library/main/deck.json"
SOURCE_REPOSITORY = "https://github.com/PLOT4ai/plot4ai-library"
SOURCE_DECK_URL = "https://github.com/PLOT4ai/plot4ai-library/blob/main/deck.json"
PLOT4AI_WEBSITE = "https://plot4.ai/"
PLOT4AI_LIBRARY = "https://plot4.ai/library"
LICENSE = "CC-BY-SA-4.0"
TYPE = "plot4ai"
NAME = "PLOT4ai"
DESCRIPTION = (
    "Practical Library Of Threats 4 Artificial Intelligence (PLOT4ai) risk cards "
    "for threat modeling responsible AI systems."
)
AUTHORS = ["PLOT4ai", "MISP Project"]
UUID_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, SOURCE_DECK_URL)
GALAXY_UUID = str(uuid.uuid5(UUID_NAMESPACE, "galaxy"))
CLUSTER_UUID = str(uuid.uuid5(UUID_NAMESPACE, "cluster"))

# Curated links to relevant existing MISP galaxies. These mappings are intentionally
# conservative and only connect PLOT4ai cards to close MITRE ATLAS / ATR concepts.
RELATED_BY_LABEL: dict[str, list[dict[str, str]]] = {
    "Data Integrity": [{"dest-uuid": "0ec538ca-589b-4e42-bcaa-06097a0d679f", "type": "related-to"}],
    "Poisoning Attacks": [
        {"dest-uuid": "0ec538ca-589b-4e42-bcaa-06097a0d679f", "type": "similar-to"},
        {"dest-uuid": "f4fc2abd-71a4-401a-a742-18fc5aeb4bc3", "type": "related-to"},
        {"dest-uuid": "e3b9d41a-d2f9-4825-942f-1c4a30b4d2f9", "type": "related-to"},
    ],
    "Model Evasion": [
        {"dest-uuid": "071df654-813a-4708-85dc-f715f785d37f", "type": "similar-to"},
        {"dest-uuid": "a7c30122-b393-4265-91b7-57cd1211e3f9", "type": "related-to"},
    ],
    "Adversarial Examples": [{"dest-uuid": "a7c30122-b393-4265-91b7-57cd1211e3f9", "type": "similar-to"}],
    "Model Inversion": [{"dest-uuid": "e19c6f8a-f1e2-46cc-9387-03a3092f01ed", "type": "similar-to"}],
    "Membership Inference": [{"dest-uuid": "86b5f486-afb8-4aa9-991f-0e24d5737f0c", "type": "similar-to"}],
    "Model Stealing": [{"dest-uuid": "f78e0ac3-6d72-42ed-b20a-e10d8c752cf6", "type": "similar-to"}],
    "AI Supply Chain Access": [{"dest-uuid": "d2cf31e0-a550-4fe0-8fdb-8941b3ac00d9", "type": "related-to"}],
    "AI Supply Chain Tools": [
        {"dest-uuid": "d2cf31e0-a550-4fe0-8fdb-8941b3ac00d9", "type": "related-to"},
        {"dest-uuid": "be6ef5c5-1ecb-486d-9743-42085bd2c256", "type": "related-to"},
        {"dest-uuid": "1f63b56d-034f-477d-ab49-399c1aa1a22a", "type": "mitigated-by"},
    ],
    "Jailbreaking": [{"dest-uuid": "172427e3-9ecc-49a3-b628-96b824cc4131", "type": "similar-to"}],
    "Prompt Injection": [
        {"dest-uuid": "19cd2d12-66ff-487c-a05c-e058b027efc9", "type": "similar-to"},
        {"dest-uuid": "7859f830-8dd6-55ee-a3c4-d942825b4294", "type": "related-to"},
        {"dest-uuid": "25be13cc-b593-5a70-bc2a-806b1b2cd544", "type": "related-to"},
    ],
    "Information Disclosure": [
        {"dest-uuid": "45d378aa-20ae-401d-bf61-7f00104eeaca", "type": "related-to"},
        {"dest-uuid": "01590c5a-255a-503b-a3cb-5016da41ae9c", "type": "related-to"},
    ],
    "Confidential Information": [{"dest-uuid": "45d378aa-20ae-401d-bf61-7f00104eeaca", "type": "related-to"}],
    "API & Model Interface Security": [{"dest-uuid": "90a420d4-3f03-4800-86c0-223c4376804a", "type": "related-to"}],
    "Fine-tuning Attacks": [{"dest-uuid": "3964ef51-6973-5f00-bdc4-5fe689c9612d", "type": "related-to"}],
    "RAG & Vector Databases": [{"dest-uuid": "3ca267ca-4224-54d0-b467-28870fbc67c5", "type": "related-to"}],
    "Agentic AI Hallucinations": [{"dest-uuid": "782c346d-9af5-4145-b6c6-b9cccdc2c950", "type": "related-to"}],
    "Misinformation": [{"dest-uuid": "53c52153-8a3f-4952-8e20-e9ab7ca899a7", "type": "related-to"}],
    "Deepfakes & Synthetic Deception": [{"dest-uuid": "7159b4d1-7681-4028-8110-8ebdb16c7700", "type": "related-to"}],
    "Security Testing": [{"dest-uuid": "01c2ec0a-e257-4a75-9e59-f71aa6362b6e", "type": "related-to"}],
    "Model Serialization": [{"dest-uuid": "9da06101-b9e9-5d87-9a2a-1227b3c0add6", "type": "related-to"}],
}

MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
URL_RE = re.compile(r"https?://[^\s)]+")


def uuid_for(*parts: str) -> str:
    return str(uuid.uuid5(UUID_NAMESPACE, "|".join(parts)))


def clean_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    value = re.sub(r"[ \t]+\n", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        item = item.strip()
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return output


def extract_markdown_links(*texts: str) -> tuple[list[str], list[str]]:
    refs: list[str] = []
    names: list[str] = []
    for text in texts:
        for name, url in MARKDOWN_LINK_RE.findall(text or ""):
            names.append(clean_text(name))
            refs.append(url.rstrip(".,"))
        refs.extend(url.rstrip(".,") for url in URL_RE.findall(text or ""))
    return dedupe(refs), dedupe(names)


def load_deck(source: str | Path) -> list[dict[str, Any]]:
    if str(source).startswith(("http://", "https://")):
        with urlopen(str(source), timeout=30) as response:  # noqa: S310 - explicit user/source URL
            return json.loads(response.read().decode("utf-8"))
    return json.loads(Path(source).read_text(encoding="utf-8"))


def build_galaxy() -> dict[str, Any]:
    return {
        "description": DESCRIPTION,
        "icon": "brain",
        "name": NAME,
        "namespace": "misp",
        "type": TYPE,
        "uuid": GALAXY_UUID,
        "version": 1,
    }


def build_cluster(deck: list[dict[str, Any]]) -> dict[str, Any]:
    values: list[dict[str, Any]] = []
    sequence = 0
    for category in deck:
        category_name = category["category"]
        category_id = category.get("id")
        colour = category.get("colour")
        for card in category.get("cards", []):
            sequence += 1
            label = clean_text(card["label"])
            explanation = clean_text(card.get("explanation", ""))
            question = clean_text(card.get("question", ""))
            recommendation = clean_text(card.get("recommendation", ""))
            sources = clean_text(card.get("sources", ""))
            description_parts = [explanation]
            if question:
                description_parts.append(f"Threat-modeling question: {question}")
            description = "\n\n".join(part for part in description_parts if part)
            refs, source_names = extract_markdown_links(sources, recommendation)
            refs = dedupe([*refs, SOURCE_DECK_URL, PLOT4AI_LIBRARY])
            meta: dict[str, Any] = {
                "external_id": f"PLOT4AI-{sequence:03d}",
                "aitypes": card.get("aitypes", []),
                "roles": card.get("roles", []),
                "categories": card.get("categories", []),
                "primary_category": category_name,
                "phases": card.get("phases", []),
                "threatif": clean_text(card.get("threatif", "")),
                "question": question,
                "recommendation": recommendation,
                "refs": refs,
                "source_repository": SOURCE_REPOSITORY,
                "source_deck": SOURCE_DECK_URL,
                "source_license": LICENSE,
            }
            if category_id is not None:
                meta["category_id"] = str(category_id)
            if colour:
                meta["colour"] = f"#{colour}"
            if sources:
                meta["source_text"] = sources
            if source_names:
                meta["source_names"] = source_names
            if card.get("cia"):
                meta["cia"] = card["cia"]
            if card.get("qr"):
                meta["qr"] = card["qr"]
            entry: dict[str, Any] = {
                "description": description,
                "meta": meta,
                "uuid": uuid_for("card", f"{sequence:03d}", label),
                "value": label,
            }
            related = RELATED_BY_LABEL.get(label)
            if related:
                entry["related"] = related
            values.append(entry)
    return {
        "authors": AUTHORS,
        "category": "ai-threat-modeling",
        "description": DESCRIPTION,
        "name": NAME,
        "source": SOURCE_DECK_URL,
        "type": TYPE,
        "uuid": CLUSTER_UUID,
        "values": values,
        "version": 1,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def validate(cluster_path: Path, galaxy_path: Path, schema_dir: Path) -> None:
    try:
        import jsonschema
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SystemExit("jsonschema is required for --validate") from exc
    cluster_schema = json.loads((schema_dir / "schema_clusters.json").read_text(encoding="utf-8"))
    galaxy_schema = json.loads((schema_dir / "schema_galaxies.json").read_text(encoding="utf-8"))
    jsonschema.validate(json.loads(cluster_path.read_text(encoding="utf-8")), cluster_schema)
    jsonschema.validate(json.loads(galaxy_path.read_text(encoding="utf-8")), galaxy_schema)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the PLOT4ai MISP galaxy and cluster.")
    parser.add_argument("--source", default=RAW_DECK_URL, help="PLOT4ai deck JSON path or URL")
    parser.add_argument("--output-dir", type=Path, default=Path("."), help="misp-galaxy repository root")
    parser.add_argument("--validate", action="store_true", help="validate generated JSON against repository schemas")
    args = parser.parse_args()

    deck = load_deck(args.source)
    if not isinstance(deck, list):
        raise SystemExit("PLOT4ai deck must be a list of categories")

    galaxy_path = args.output_dir / "galaxies" / f"{TYPE}.json"
    cluster_path = args.output_dir / "clusters" / f"{TYPE}.json"
    write_json(galaxy_path, build_galaxy())
    write_json(cluster_path, build_cluster(deck))
    if args.validate:
        validate(cluster_path, galaxy_path, args.output_dir)
    print(f"Wrote {galaxy_path}")
    print(f"Wrote {cluster_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
