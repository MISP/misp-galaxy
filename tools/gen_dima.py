#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import subprocess
import uuid
from pathlib import Path
from urllib.request import urlopen

BASE_URL = "https://raw.githubusercontent.com/M82-project/DIMA/main/docs/data"
FILES = ["ACT", "DETECT", "INFORM", "MEMORISE"]
NAMESPACE = uuid.UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")


def stable_uuid(*parts: str) -> str:
    return str(uuid.uuid5(NAMESPACE, ":".join(parts)))


def fetch_phase(phase: str) -> dict:
    with urlopen(f"{BASE_URL}/{phase}.json") as response:  # nosec B310
        return json.load(response)


def build_cluster(data_by_phase: list[dict]) -> dict:
    values = []
    for phase_data in data_by_phase:
        phase = phase_data["phase"]
        for tactic in phase_data.get("tactics", []):
            tactic_id = tactic.get("id", "")
            tactic_name = tactic.get("name", "")
            for technique in tactic.get("techniques", []):
                technique_id = technique.get("id", "")
                technique_name = technique.get("name", "")
                description = technique.get("description") or ""

                section_chunks = []
                for section in technique.get("sections", []):
                    title = section.get("title", "Section")
                    items = section.get("items", [])
                    if items:
                        section_chunks.append(f"{title}: " + " | ".join(items))
                if section_chunks:
                    description = f"{description}\n\n".strip() + "\n" + "\n".join(section_chunks)

                values.append(
                    {
                        "value": technique_name,
                        "uuid": stable_uuid("dima-techniques", technique_id, technique_name),
                        "description": description,
                        "meta": {
                            "external_id": technique_id,
                            "tactic_id": tactic_id,
                            "tactic_name": tactic_name,
                            "phase": phase,
                            "kill_chain": [f"tactics:{phase} - {tactic_name}"],
                            "refs": [
                                f"https://github.com/M82-project/DIMA/blob/main/docs/data/{phase}.json"
                            ],
                        },
                    }
                )

    return {
        "name": "Techniques",
        "description": "DIMA is a social engineering and cognitive manipulation framework organized by phase, tactic, and technique.",
        "category": "dima",
        "type": "dima-techniques",
        "source": "https://github.com/M82-project/DIMA",
        "authors": ["M82 Project"],
        "uuid": stable_uuid("cluster", "dima-techniques"),
        "values": values,
    }


def build_galaxy(data_by_phase: list[dict], version: int = 1) -> dict:
    kill_chain = []
    for phase_data in data_by_phase:
        phase = phase_data["phase"]
        for tactic in phase_data.get("tactics", []):
            kill_chain.append(f"{phase} - {tactic.get('name', '')}")

    return {
        "name": "Techniques",
        "description": "DIMA is a social engineering and cognitive manipulation framework organized by phase, tactic, and technique.",
        "namespace": "dima",
        "type": "dima-techniques",
        "uuid": stable_uuid("galaxy", "dima-techniques"),
        "version": version,
        "icon": "project-diagram",
        "kill_chain_order": {"tactics": kill_chain},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MISP galaxy and cluster files from DIMA JSON data")
    parser.add_argument("--galaxy-output", default="galaxies/dima-techniques.json", help="path to galaxy output JSON")
    parser.add_argument("--cluster-output", default="clusters/dima-techniques.json", help="path to cluster output JSON")
    args = parser.parse_args()

    data_by_phase = [fetch_phase(phase) for phase in FILES]

    current_version = 0
    galaxy_output = Path(args.galaxy_output)
    if galaxy_output.exists():
        existing_galaxy = json.loads(galaxy_output.read_text(encoding="utf-8"))
        current_version = int(existing_galaxy.get("version", 0))

    galaxy = build_galaxy(data_by_phase, version=current_version + 1)
    cluster = build_cluster(data_by_phase)

    galaxy_output.write_text(json.dumps(galaxy, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    Path(args.cluster_output).write_text(json.dumps(cluster, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    subprocess.run(["./jq_all_the_things.sh"], check=True)


if __name__ == "__main__":
    main()
