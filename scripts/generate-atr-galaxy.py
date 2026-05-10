#!/usr/bin/env python3
"""Generate MISP galaxy + cluster JSON files for agent-threat-rules.

Reads ATR rule YAML files, emits:
- galaxies/agent-threat-rules.json (metadata)
- clusters/agent-threat-rules.json (336 entries)

UUIDs are deterministic (UUID5) so regenerating is byte-stable.
Run from misp-galaxy fork root, with --rules-dir pointing at the
agent-threat-rules clone.
"""
import argparse
import json
import sys
import uuid
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

GALAXY_NS = uuid.UUID("6f7a8b9c-1d2e-4f5a-9b8c-7e6d5f4a3b2c")  # stable namespace
CATEGORIES = [
    "prompt-injection",
    "tool-poisoning",
    "context-exfiltration",
    "agent-manipulation",
    "privilege-escalation",
    "excessive-autonomy",
    "data-poisoning",
    "model-abuse",
    "skill-compromise",
]

GALAXY_UUID = "5b3d8c2e-7a1f-4e9b-8c5d-2a4f6b9e8c1d"
CLUSTER_UUID = "9e2c5a7b-3f8d-4b1c-a6e9-7d5c8b2f4a3e"


def load_rules(rules_dir: Path) -> list[dict]:
    rules = []
    for yaml_path in sorted(rules_dir.glob("**/*.yaml")):
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                rule = yaml.safe_load(f)
            if not isinstance(rule, dict) or "id" not in rule:
                continue
            rules.append(rule)
        except Exception as e:
            print(f"skip {yaml_path}: {e}", file=sys.stderr)
    return rules


def build_galaxy() -> dict:
    return {
        "description": "Agent Threat Rules (ATR) — open detection standard for AI agent threats covering prompt injection, tool poisoning, context exfiltration, and 6 other attack classes against MCP servers, skill manifests, and agent runtimes. 336 rules across 9 categories.",
        "icon": "shield-virus",
        "kill_chain_order": {
            "agent-threat": CATEGORIES,
        },
        "name": "Agent Threat Rules",
        "namespace": "agent-threat-rules",
        "type": "agent-threat-rules",
        "uuid": GALAXY_UUID,
        "version": 1,
    }


def category_of(rule: dict) -> str:
    cat = (rule.get("tags") or {}).get("category", "")
    if cat in CATEGORIES:
        return cat
    return "skill-compromise"  # safe fallback for any uncategorised


def cve_refs(rule: dict) -> list[str]:
    refs = (rule.get("references") or {}).get("cve") or []
    return [r for r in refs if isinstance(r, str)]


def github_url(rule_id: str, category: str) -> str:
    return f"https://github.com/Agent-Threat-Rule/agent-threat-rules/tree/main/rules/{category}"


def build_value(rule: dict) -> dict:
    rule_id = rule["id"]
    title = rule.get("title", rule_id)
    desc = (rule.get("description") or "").strip()
    if not desc:
        desc = title
    cat = category_of(rule)
    severity = rule.get("severity", "medium")

    meta: dict = {
        "external_id": rule_id,
        "kill_chain": [f"agent-threat:{cat}"],
        "refs": [github_url(rule_id, cat)],
        "severity": severity,
    }
    cves = cve_refs(rule)
    if cves:
        meta["cve"] = cves

    owasp_llm = (rule.get("references") or {}).get("owasp_llm") or []
    if owasp_llm:
        meta["owasp_llm"] = owasp_llm
    mitre_atlas = (rule.get("references") or {}).get("mitre_atlas") or []
    if mitre_atlas:
        meta["mitre_atlas"] = mitre_atlas

    return {
        "description": desc,
        "meta": meta,
        "uuid": str(uuid.uuid5(GALAXY_NS, rule_id)),
        "value": f"{title} - {rule_id}",
    }


def build_cluster(rules: list[dict]) -> dict:
    values = sorted(
        (build_value(r) for r in rules),
        key=lambda v: v["meta"]["external_id"],
    )
    return {
        "authors": ["Adam Lin", "ATR Community"],
        "category": "agent-threat-rules",
        "description": "Open detection rules for AI agent threats — prompt injection, tool poisoning, MCP server attacks, skill compromise. Each cluster value is one ATR rule with category, severity, and CVE/OWASP/MITRE ATLAS references where mapped.",
        "name": "Agent Threat Rules",
        "source": "https://github.com/Agent-Threat-Rule/agent-threat-rules",
        "type": "agent-threat-rules",
        "uuid": CLUSTER_UUID,
        "values": values,
        "version": 1,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--rules-dir", required=True, help="Path to agent-threat-rules/rules")
    p.add_argument("--galaxy-out", default="galaxies/agent-threat-rules.json")
    p.add_argument("--cluster-out", default="clusters/agent-threat-rules.json")
    args = p.parse_args()

    rules_dir = Path(args.rules_dir).resolve()
    if not rules_dir.is_dir():
        print(f"rules-dir not found: {rules_dir}", file=sys.stderr)
        return 1

    rules = load_rules(rules_dir)
    print(f"loaded {len(rules)} rules from {rules_dir}")

    galaxy = build_galaxy()
    cluster = build_cluster(rules)

    Path(args.galaxy_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.cluster_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.galaxy_out, "w", encoding="utf-8") as f:
        json.dump(galaxy, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(args.cluster_out, "w", encoding="utf-8") as f:
        json.dump(cluster, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"wrote {args.galaxy_out}")
    print(f"wrote {args.cluster_out} ({len(cluster['values'])} values)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
