#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate the software-vendor galaxy/cluster from GitHub organizations.

By default this script queries the top 1000 GitHub organizations by followers
within the scope used for this galaxy and writes:
- galaxies/software-vendor.json
- clusters/software-vendor.json

Usage examples:
  python3 gen_software_vendor.py
  python3 gen_software_vendor.py --limit 200 --min-followers 500
  python3 gen_software_vendor.py --output-dir /tmp/misp-galaxy

Optional environment variable:
  GITHUB_TOKEN: Used for authenticated requests and higher rate limits.
"""

import argparse
import json
import os
import time
import uuid
from pathlib import Path

import requests


GALAXY_UUID = "d2c5f795-087c-4d15-a287-7ee0ae353875"
CLUSTER_UUID = "0a2825ac-2a59-481e-8d1f-83856a3b45e1"
ENTRY_UUID_NAMESPACE = uuid.UUID("2b0d4f2f-9d37-4dc4-9e67-ecf3c9600f4d")


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "Accept": "application/vnd.github+json",
        "User-Agent": "misp-galaxy-software-vendor-generator",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    return session


def fetch_top_orgs(session: requests.Session, limit: int, min_followers: int, sleep_seconds: float):
    orgs = []
    page = 1
    per_page = 100
    query = f"type:org followers:>={min_followers}"

    while len(orgs) < limit:
        response = session.get(
            "https://api.github.com/search/users",
            params={
                "q": query,
                "sort": "followers",
                "order": "desc",
                "per_page": per_page,
                "page": page,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        orgs.extend(items)
        page += 1

        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    return orgs[:limit]


def generate_cluster_values(orgs):
    values = []
    for rank, org in enumerate(orgs, start=1):
        login = org["login"]
        values.append(
            {
                "value": login,
                "description": (
                    "Open-source organization active on GitHub. "
                    f"Ranked #{rank} by GitHub follower count within the query scope "
                    "(type:org, followers>=200)."
                ),
                "uuid": str(uuid.uuid5(ENTRY_UUID_NAMESPACE, login.lower())),
                "meta": {
                    "official-refs": [org["html_url"]],
                    "refs": [org["url"]],
                    "products": [f"{login} public GitHub repositories"],
                },
            }
        )
    return values


def build_cluster(values):
    return {
        "authors": ["Various"],
        "category": "actor",
        "description": (
            "Top 1000 open-source organizations on GitHub (ranked by followers) "
            "with reference links and repository portfolio metadata."
        ),
        "name": "Software Vendor",
        "source": "MISP Project",
        "type": "software-vendor",
        "uuid": CLUSTER_UUID,
        "values": values,
        "version": 1,
    }


def build_galaxy():
    return {
        "description": (
            "Top 1000 open-source organizations on GitHub with references to their "
            "main organization pages and repository portfolio metadata."
        ),
        "icon": "building",
        "name": "Software Vendor",
        "namespace": "misp",
        "type": "software-vendor",
        "uuid": GALAXY_UUID,
        "version": 1,
    }


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Generate software-vendor galaxy and cluster files.")
    parser.add_argument("--limit", type=int, default=1000, help="Number of organizations to include.")
    parser.add_argument("--min-followers", type=int, default=200, help="GitHub search minimum followers filter.")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1]),
        help="Repository root output directory containing galaxies/ and clusters/.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=1.0,
        help="Pause duration between GitHub API page requests.",
    )
    args = parser.parse_args()

    session = build_session()
    orgs = fetch_top_orgs(
        session=session,
        limit=args.limit,
        min_followers=args.min_followers,
        sleep_seconds=args.sleep_seconds,
    )

    if not orgs:
        raise RuntimeError("No organizations were retrieved from GitHub API.")

    values = generate_cluster_values(orgs)
    output_dir = Path(args.output_dir)
    write_json(output_dir / "clusters" / "software-vendor.json", build_cluster(values))
    write_json(output_dir / "galaxies" / "software-vendor.json", build_galaxy())

    print(f"Generated software-vendor galaxy + cluster with {len(values)} entries in {output_dir}.")


if __name__ == "__main__":
    main()
