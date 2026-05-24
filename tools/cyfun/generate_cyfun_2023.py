#!/usr/bin/env python3
"""Generate a metadata-first MISP galaxy for CCB CyberFundamentals Framework 2023.

This generator intentionally does not reproduce the verbatim normative requirements or
extended guidance from the source PDFs. It extracts control identifiers and provenance
only, and uses the official PDFs as referenced authoritative sources.

Requirements: Python >= 3.9, PyMuPDF (fitz), jsonschema (for --validate).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import fitz

FRAMEWORK_VERSION = "2023"
DOCUMENT_VERSION = "2023-03-01"
LANDING_PAGE = "https://atwork.safeonweb.be/tools-resources/cyberfundamentals-framework"
SOURCE_PDFS = {
    "Small": "https://atwork.safeonweb.be/sites/default/files/2025-10/CCB_CyFun2023_Booklet-SMALL_E%20%5BLR-web%5D.pdf",
    "Basic": "https://atwork.safeonweb.be/sites/default/files/2025-10/CCB_CyFun2023_Booklet-BASIC_E%20%5BLR-web%5D.pdf",
    "Important": "https://atwork.safeonweb.be/sites/default/files/2025-10/CCB_CyFun2023_Booklet-IMPORTANT_E%20%5BLR-web%5D.pdf",
    "Essential": "https://atwork.safeonweb.be/sites/default/files/2025-10/CCB_CyFun2023_Booklet-ESSENTIAL_E%20%5BLR-web%5D.pdf",
}
LOCAL_FILENAMES = {
    "Small": "CyFun2023-SMALL.pdf",
    "Basic": "CyFun2023-BASIC.pdf",
    "Important": "CyFun2023-IMPORTANT.pdf",
    "Essential": "CyFun2023-ESSENTIAL.pdf",
}
BODY_PAGES = {"Basic": (8, 38), "Important": (10, 76), "Essential": (10, 95)}
SMALL_BODY_PAGES = (6, 9)
FUNCTIONS = {"ID": "Identify", "PR": "Protect", "DE": "Detect", "RS": "Respond", "RC": "Recover"}
CATEGORIES = {
    "ID.AM": "Asset Management", "ID.BE": "Business Environment", "ID.GV": "Governance",
    "ID.RA": "Risk Assessment", "ID.RM": "Risk Management Strategy", "ID.SC": "Supply Chain Risk Management",
    "PR.AC": "Identity Management and Access Control", "PR.AT": "Awareness and Training", "PR.DS": "Data Security",
    "PR.IP": "Information Protection Processes and Procedures", "PR.MA": "Maintenance", "PR.PT": "Protective Technology",
    "DE.AE": "Anomalies and Events", "DE.CM": "Security Continuous Monitoring", "DE.DP": "Detection Processes",
    "RS.RP": "Response Planning", "RS.CO": "Communications", "RS.AN": "Analysis", "RS.MI": "Mitigation",
    "RS.IM": "Improvements", "RC.RP": "Recovery Planning", "RC.IM": "Improvements", "RC.CO": "Communications",
}
SMALL_THEMES = {
    "SMALL-1": "Authentication", "SMALL-2": "Patch Management", "SMALL-3": "Endpoint Protection",
    "SMALL-4": "Network Security", "SMALL-5": "Backup", "SMALL-6": "Privileged Access",
    "SMALL-7": "Preparedness",
}
# Control-level mapping of the normative key-measure lists in the official annexes.
# Counts record how many listed key-measure requirements are associated with that control.
KEY_MEASURE_CONTROLS = {
    "Basic": {
        "PR.AC-1": 1, "PR.AC-3": 1, "PR.AC-4": 4, "PR.AC-5": 2, "PR.IP-4": 1,
        "PR.MA-1": 1, "PR.PT-1": 1, "DE.AE-3": 1, "DE.CM-4": 1,
    },
    "Important": {
        "ID.AM-6": 1, "PR.AC-3": 1, "PR.AC-5": 2, "PR.DS-5": 1, "PR.IP-1": 1,
        "DE.CM-1": 1, "RS.AN-5": 1,
    },
    "Essential": {
        "ID.SC-3": 2, "PR.AC-7": 1, "PR.MA-1": 3, "PR.PT-2": 1, "DE.AE-1": 1,
    },
}
KEY_MEASURE_SCOPE = {
    "Small": [], "Basic": ["Basic"], "Important": ["Basic", "Important"],
    "Essential": ["Basic", "Important", "Essential"],
}
UUID_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, LANDING_PAGE + "|CyberFundamentals|2023")


def clean_text(text: str) -> str:
    text = text.replace("\x02", "").replace("\x07", "").replace("\ufeff", "").replace("\u00ad", "")
    text = text.replace("\u2002", " ").replace("\u00a0", " ")
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
    return re.sub(r"\s+", " ", text).strip()


def control_function(code: str) -> str:
    return FUNCTIONS[code[:2]]


def control_category_code(code: str) -> str:
    return code.rsplit("-", 1)[0]


def uuid_for(*parts: str) -> str:
    return str(uuid.uuid5(UUID_NAMESPACE, "|".join(parts)))


def _page_blocks(doc: fitz.Document, page_number: int) -> Tuple[List[dict], bool]:
    page = doc[page_number - 1]
    raw_blocks = page.get_text("blocks", sort=True)
    page_text = clean_text(page.get_text("text"))
    heading_candidates = []
    for block in raw_blocks:
        text = clean_text(block[4])
        if re.match(r"^((?:ID|PR|DE|RS|RC)\.[A-Z]{2}-\d+)\s+", text):
            heading_candidates.append((block[1], text))
    has_sidebar = "FRAMEWORK" in page_text
    likely_divider = (
        not heading_candidates
        and "Guidance" not in page_text
        and " shall " not in f" {page_text} "
        and any(function.upper() in page_text.upper() for function in FUNCTIONS.values())
        and len(page_text) < 350
    )
    if likely_divider:
        return [], True
    first_heading_y = min((y for y, _ in heading_candidates), default=300) if has_sidebar else None
    blocks: List[dict] = []
    for x0, y0, _x1, _y1, raw, *_ in raw_blocks:
        text = clean_text(raw)
        if not text or y0 > 785:
            continue
        if has_sidebar and y0 < first_heading_y - 1:
            continue
        blocks.append({"text": text, "page": page_number, "x0": x0, "y0": y0})
    return blocks, False


def parse_coded_level(pdf_path: Path, level: str) -> List[dict]:
    start_page, end_page = BODY_PAGES[level]
    doc = fitz.open(pdf_path)
    records: List[dict] = []
    current = None
    for page_number in range(start_page, end_page + 1):
        blocks, divider = _page_blocks(doc, page_number)
        if divider:
            continue
        for block in blocks:
            match = re.match(r"^((?:ID|PR|DE|RS|RC)\.[A-Z]{2}-\d+)\s+", block["text"])
            if match:
                if current:
                    records.append(current)
                current = {"code": match.group(1), "pages": [page_number], "body_parts": []}
            elif current:
                current["body_parts"].append(block["text"])
                if page_number not in current["pages"]:
                    current["pages"].append(page_number)
    if current:
        records.append(current)
    deduped = []
    seen = set()
    for record in records:
        if record["code"] not in seen:
            seen.add(record["code"])
            deduped.append(record)
    return deduped


def parse_small(pdf_path: Path) -> List[dict]:
    doc = fitz.open(pdf_path)
    records: List[dict] = []
    for page_number in range(SMALL_BODY_PAGES[0], SMALL_BODY_PAGES[1] + 1):
        for block in doc[page_number - 1].get_text("blocks", sort=True):
            text = clean_text(block[4])
            match = re.match(r"^(\d+)\.\s+", text)
            if match:
                records.append({"code": f"SMALL-{match.group(1)}", "pages": [page_number]})
    return records


def page_display(pages: Iterable[int]) -> List[str]:
    return [str(page - 2) for page in pages]


def status_from_record(record: dict) -> str:
    text = clean_text(" ".join(record.get("body_parts", []))).lower()
    if "no requirements are identified" in text or "no additional requirements are identified" in text:
        return "guidance-only-or-no-additional-requirement"
    return "requirements-and-guidance"


def scoped_key_measure_metadata(level: str, code: str) -> Tuple[List[str], int]:
    tiers = []
    count = 0
    for tier in KEY_MEASURE_SCOPE[level]:
        if code in KEY_MEASURE_CONTROLS[tier]:
            tiers.append(tier)
            count += KEY_MEASURE_CONTROLS[tier][code]
    return tiers, count


def build_records(pdf_dir: Path) -> Dict[str, List[dict]]:
    data = {"Small": parse_small(pdf_dir / LOCAL_FILENAMES["Small"])}
    for level in ("Basic", "Important", "Essential"):
        data[level] = parse_coded_level(pdf_dir / LOCAL_FILENAMES[level], level)
    return data


def build_catalogue(records: Dict[str, List[dict]]) -> dict:
    by_code: Dict[str, dict] = {}
    for level in ("Small", "Basic", "Important", "Essential"):
        for record in records[level]:
            code = record["code"]
            entry = by_code.setdefault(code, {"levels": [], "page_meta": []})
            entry["levels"].append(level)
            pages = ",".join(page_display(record["pages"]))
            entry["page_meta"].append(f"{level}:{pages}")
    values = []
    for code in sorted(by_code, key=lambda c: (c.startswith("SMALL-"), c)):
        info = by_code[code]
        if code.startswith("SMALL-"):
            theme = SMALL_THEMES[code]
            description = f"CyberFundamentals 2023 Small catalogue item in the {theme} theme. Consult the official PDF for normative wording and guidance."
            meta = {
                "external_id": code, "framework_version": FRAMEWORK_VERSION, "document_version": DOCUMENT_VERSION,
                "assurance_levels": info["levels"], "theme": theme, "source_pages": info["page_meta"],
                "refs": [SOURCE_PDFS["Small"], LANDING_PAGE], "content_policy": "authoritative-text-in-official-source",
            }
        else:
            category_code = control_category_code(code)
            tiers = [tier for tier, codes in KEY_MEASURE_CONTROLS.items() if code in codes]
            description = f"CyberFundamentals 2023 catalogue control {code}. Consult the official PDF documents for normative wording and guidance."
            meta = {
                "external_id": code, "framework_version": FRAMEWORK_VERSION, "document_version": DOCUMENT_VERSION,
                "assurance_levels": info["levels"], "cyfun_function": control_function(code),
                "category_code": category_code, "category_name": CATEGORIES[category_code],
                "source_pages": info["page_meta"], "key_measure_tiers": tiers,
                "refs": [LANDING_PAGE] + [SOURCE_PDFS[level] for level in info["levels"]],
                "content_policy": "authoritative-text-in-official-source",
            }
        values.append({
            "uuid": uuid_for("catalogue", code), "value": f"CyFun 2023 - {code}",
            "description": description, "meta": meta,
        })
    return {
        "authors": ["Centre for Cybersecurity Belgium (source framework)", "MISP Project (galaxy format)"],
        "category": "cybersecurity-framework", "description": "Normalized CyberFundamentals 2023 control catalogue. Values preserve identifiers, assurance-level availability, official provenance, and key-measure mapping without reproducing normative text.",
        "name": "CyberFundamentals 2023 Control Catalogue", "source": LANDING_PAGE,
        "type": "cyfun-control-catalogue-2023", "uuid": uuid_for("cluster", "catalogue"), "version": 1, "values": values,
    }


def build_requirements(records: Dict[str, List[dict]], pdf_dir: Path) -> dict:
    values = []
    level_tabs = {
        "CyFun-Small": list(SMALL_THEMES.values()),
        "CyFun-Basic": ["Identify", "Protect", "Detect", "Respond", "Recover"],
        "CyFun-Important": ["Identify", "Protect", "Detect", "Respond", "Recover"],
        "CyFun-Essential": ["Identify", "Protect", "Detect", "Respond", "Recover"],
    }
    for level in ("Small", "Basic", "Important", "Essential"):
        for record in records[level]:
            code = record["code"]
            pages = record["pages"]
            if code.startswith("SMALL-"):
                theme = SMALL_THEMES[code]
                description = f"CyberFundamentals 2023 Small item in the {theme} theme. Normative content remains in the official source document."
                meta = {
                    "external_id": code, "assurance_level": level, "theme": theme,
                    "kill_chain": [f"CyFun-Small:{theme}"], "framework_version": FRAMEWORK_VERSION,
                    "document_version": DOCUMENT_VERSION, "source_pdf_pages": [str(p) for p in pages],
                    "source_document_pages": page_display(pages), "refs": [SOURCE_PDFS[level], LANDING_PAGE],
                    "content_policy": "authoritative-text-in-official-source",
                }
            else:
                category_code = control_category_code(code)
                tiers, requirement_count = scoped_key_measure_metadata(level, code)
                status = status_from_record(record)
                description = f"CyberFundamentals 2023 {level} control {code}. Normative requirements and guidance remain in the official source document."
                meta = {
                    "external_id": code, "assurance_level": level, "cyfun_function": control_function(code),
                    "category_code": category_code, "category_name": CATEGORIES[category_code],
                    "kill_chain": [f"CyFun-{level}:{control_function(code)}"],
                    "framework_version": FRAMEWORK_VERSION, "document_version": DOCUMENT_VERSION,
                    "source_pdf_pages": [str(p) for p in pages], "source_document_pages": page_display(pages),
                    "requirement_status": status, "is_key_measure": "true" if tiers else "false",
                    "key_measure_tiers_in_scope": tiers, "key_measure_requirement_count_in_scope": str(requirement_count),
                    "refs": [SOURCE_PDFS[level], LANDING_PAGE], "content_policy": "authoritative-text-in-official-source",
                }
            values.append({
                "uuid": uuid_for("requirements", level, code), "value": f"CyFun 2023 {level} - {code}",
                "description": description, "meta": meta,
                "related": [{"dest-uuid": uuid_for("catalogue", code), "type": "is-instance-of"}],
            })
    cluster = {
        "authors": ["Centre for Cybersecurity Belgium (source framework)", "MISP Project (galaxy format)"],
        "category": "cybersecurity-framework", "description": "CyberFundamentals 2023 assurance-level control matrix for MISP. Each cluster value is a level-specific control instance with provenance and key-measure metadata; normative text is referenced, not embedded.",
        "name": "CyberFundamentals 2023 Assurance Requirements", "source": LANDING_PAGE,
        "type": "cyfun-assurance-requirements-2023", "uuid": uuid_for("cluster", "requirements"), "version": 1, "values": values,
    }
    galaxy = {
        "description": cluster["description"], "icon": "map", "kill_chain_order": level_tabs,
        "name": cluster["name"], "namespace": "ccb", "type": cluster["type"],
        "uuid": uuid_for("galaxy", "requirements"), "version": 1,
    }
    return cluster, galaxy


def build_galaxies(pdf_dir: Path, output_dir: Path) -> Dict[str, int]:
    records = build_records(pdf_dir)
    catalogue_cluster = build_catalogue(records)
    catalogue_galaxy = {
        "description": catalogue_cluster["description"], "icon": "list", "name": catalogue_cluster["name"],
        "namespace": "ccb", "type": catalogue_cluster["type"], "uuid": uuid_for("galaxy", "catalogue"), "version": 1,
    }
    requirements_cluster, requirements_galaxy = build_requirements(records, pdf_dir)
    (output_dir / "galaxies").mkdir(parents=True, exist_ok=True)
    (output_dir / "clusters").mkdir(parents=True, exist_ok=True)
    for target, payload in [
        (output_dir / "galaxies" / "cyfun-control-catalogue-2023.json", catalogue_galaxy),
        (output_dir / "clusters" / "cyfun-control-catalogue-2023.json", catalogue_cluster),
        (output_dir / "galaxies" / "cyfun-assurance-requirements-2023.json", requirements_galaxy),
        (output_dir / "clusters" / "cyfun-assurance-requirements-2023.json", requirements_cluster),
    ]:
        target.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return {level: len(rows) for level, rows in records.items()} | {
        "catalogue_values": len(catalogue_cluster["values"]), "matrix_values": len(requirements_cluster["values"])
    }


def validate(output_dir: Path, schema_dir: Path) -> None:
    import jsonschema
    cluster_schema = json.loads((schema_dir / "schema_clusters.json").read_text(encoding="utf-8"))
    galaxy_schema = json.loads((schema_dir / "schema_galaxies.json").read_text(encoding="utf-8"))
    for path in sorted((output_dir / "clusters").glob("*.json")):
        jsonschema.validate(json.loads(path.read_text(encoding="utf-8")), cluster_schema)
    for path in sorted((output_dir / "galaxies").glob("*.json")):
        jsonschema.validate(json.loads(path.read_text(encoding="utf-8")), galaxy_schema)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf-dir", type=Path, required=True, help="Directory containing the four official PDF files")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory containing galaxies/ and clusters/")
    parser.add_argument("--validate", type=Path, help="Directory holding official schema_clusters.json and schema_galaxies.json")
    args = parser.parse_args()
    counts = build_galaxies(args.pdf_dir, args.output_dir)
    if args.validate:
        validate(args.output_dir, args.validate)
    print(json.dumps(counts, sort_keys=True))
    return 0

if __name__ == "__main__":
    sys.exit(main())
