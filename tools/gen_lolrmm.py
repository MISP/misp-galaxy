#!/usr/bin/env python3

import argparse
import json
import uuid
from pathlib import Path
from urllib.request import urlopen

SOURCE_URL = "https://lolrmm.io/api/rmm_tools.json"
GALAXY_TYPE = "rmm-tool"
UUID_NAMESPACE = uuid.UUID("8c4f8f3a-1f65-4b57-a1f0-d14ce36f6e7f")


def stable_uuid(name: str) -> str:
    return str(uuid.uuid5(UUID_NAMESPACE, name.strip().lower()))


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def clean_list(values):
    seen = set()
    out = []
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def build_meta(entry):
    meta = {}

    details = entry.get("Details", {})
    artifacts = entry.get("Artifacts", {})

    refs = clean_list(as_list(entry.get("References")))
    website = str(details.get("Website", "")).strip()
    if website:
        refs.append(website)
    detections = [d for d in as_list(entry.get("Detections")) if isinstance(d, dict)]
    refs.extend(clean_list([d.get("Sigma") or d.get("AQL") for d in detections]))
    refs = clean_list(refs)
    if refs:
        meta["refs"] = refs

    category = str(entry.get("Category", "")).strip()
    if category:
        meta["category"] = category

    author = str(entry.get("Author", "")).strip()
    if author:
        meta["author"] = author

    created = str(entry.get("Created", "")).strip()
    if created:
        meta["created"] = created

    last_modified = str(entry.get("LastModified", "")).strip()
    if last_modified:
        meta["last_modified"] = last_modified

    supported_os = clean_list(as_list(details.get("SupportedOS")))
    if supported_os:
        meta["supported_os"] = supported_os

    capabilities = clean_list(as_list(details.get("Capabilities")))
    if capabilities:
        meta["capabilities"] = capabilities

    installation_paths = clean_list(as_list(details.get("InstallationPaths")))
    if installation_paths:
        meta["installation_paths"] = installation_paths

    domains = []
    ports = []
    for network in as_list(artifacts.get("Network")):
        if not isinstance(network, dict):
            continue
        domains.extend(as_list(network.get("Domains")))
        ports.extend(as_list(network.get("Ports")))

    domains = clean_list(domains)
    if domains:
        meta["domains"] = domains

    ports = clean_list(ports)
    if ports:
        meta["ports"] = ports

    detection_descriptions = clean_list([d.get("Description") for d in detections])
    if detection_descriptions:
        meta["detection_descriptions"] = detection_descriptions

    acknowledgements = []
    for ack in as_list(entry.get("Acknowledgement")):
        if not isinstance(ack, dict):
            continue
        person = str(ack.get("Person", "")).strip()
        handle = str(ack.get("Handle", "")).strip()
        if person and handle:
            acknowledgements.append(f"{person} ({handle})")
        elif person:
            acknowledgements.append(person)
        elif handle:
            acknowledgements.append(handle)

    acknowledgements = clean_list(acknowledgements)
    if acknowledgements:
        meta["acknowledgements"] = acknowledgements

    for field in ("Privileges", "Free", "Verification"):
        value = details.get(field)
        if value not in (None, ""):
            meta[field.lower()] = str(value).strip().lower() if isinstance(value, bool) else str(value).strip()

    return meta


def build_cluster_values(entries):
    values = []
    for entry in entries:
        name = str(entry.get("Name", "")).strip()
        if not name:
            continue

        description = str(entry.get("Description", "")).strip().replace("\r\n", "\n")
        cluster = {
            "value": name,
            "uuid": stable_uuid(f"cluster:{name}"),
        }
        if description:
            cluster["description"] = description

        meta = build_meta(entry)
        if meta:
            cluster["meta"] = meta

        values.append(cluster)

    values.sort(key=lambda c: c["value"].lower())
    return values


def main():
    parser = argparse.ArgumentParser(description="Generate MISP galaxy and cluster files for LOLRMM tools.")
    parser.add_argument("--input", default=SOURCE_URL, help="URL or local path to LOLRMM JSON data")
    parser.add_argument("--output-dir", default=".", help="Repository root output directory")
    parser.add_argument("--version", type=int, default=1, help="Galaxy/cluster version")
    args = parser.parse_args()

    input_value = args.input
    if input_value.startswith("http://") or input_value.startswith("https://"):
        with urlopen(input_value) as response:
            data = json.loads(response.read().decode("utf-8"))
    else:
        data = json.loads(Path(input_value).read_text(encoding="utf-8"))

    values = build_cluster_values(data)

    cluster = {
        "authors": ["MISP Project", "LOLRMM Contributors"],
        "category": "tool",
        "description": "Remote monitoring and management tools listed by LOLRMM.",
        "name": "RMM tools",
        "source": "https://lolrmm.io/",
        "type": GALAXY_TYPE,
        "uuid": stable_uuid("cluster-root:rmm-tools"),
        "values": values,
        "version": args.version,
    }

    galaxy = {
        "description": "Remote monitoring and management tools that can be abused by threat actors.",
        "icon": "user-secret",
        "name": "RMM tools",
        "namespace": "misp",
        "type": GALAXY_TYPE,
        "uuid": stable_uuid("galaxy:rmm-tools"),
        "version": args.version,
    }

    output_dir = Path(args.output_dir)
    cluster_path = output_dir / "clusters" / f"{GALAXY_TYPE}.json"
    galaxy_path = output_dir / "galaxies" / f"{GALAXY_TYPE}.json"

    cluster_path.write_text(json.dumps(cluster, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    galaxy_path.write_text(json.dumps(galaxy, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote {cluster_path} and {galaxy_path} with {len(values)} entries.")


if __name__ == "__main__":
    main()
