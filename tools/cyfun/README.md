# CyberFundamentals 2023 MISP Galaxy - metadata-first package

This package represents the **Centre for Cybersecurity Belgium (CCB) CyberFundamentals Framework 2023** in the MISP galaxy format.

## Included galaxies

- `cyfun-control-catalogue-2023`: one normalized entry per control identifier, with the assurance levels in which it appears and its official-source provenance.
- `cyfun-assurance-requirements-2023`: a matrix-oriented galaxy with one entry per assurance-level/control instance. It includes four tabs: Small, Basic, Important, and Essential.

## Coverage

| Document | Level-specific cluster values |
| --- | ---: |
| Small | 7 |
| Basic | 33 |
| Important | 93 |
| Essential | 100 |
| **Assurance matrix total** | **233** |
| **Normalized catalogue values** | **107** |

The catalogue contains 100 NIST-CSF-style coded controls across Basic/Important/Essential and 7 Small measures.

## Metadata preserved in MISP

Each applicable cluster value includes the CyFun control identifier, assurance level, CyFun function, category code/name, official PDF page provenance, official references, document/framework version, guidance/requirement-presence status, and key-measure tier mapping. The assurance matrix value links back to the normalized catalogue value via a `related` relationship.

## Why normative text and guidance are referenced rather than embedded

The official PDFs state that texts and other document elements are protected by copyright and that extraction/reproduction is authorised for non-commercial purposes when the source is acknowledged. To make this package suitable as a redistribution-ready MISP contribution without assuming downstream licensing conditions, it contains identifiers and derived/provenance metadata while referring users to the official PDFs for normative wording and guidance.

Before distributing a text-enriched version containing extensive verbatim requirements or guidance, confirm the applicable permission or licence with CCB.

## MISP installation layout

Copy the JSON files into the corresponding MISP galaxy directories:

```text
galaxies/cyfun-control-catalogue-2023.json
galaxies/cyfun-assurance-requirements-2023.json
clusters/cyfun-control-catalogue-2023.json
clusters/cyfun-assurance-requirements-2023.json
```

The file basenames in `galaxies/` and `clusters/` deliberately match, as expected by the MISP galaxy repository conventions.

## Generation and validation

The included generator is deterministic: UUIDs are UUIDv5 values derived from the official framework landing page, framework year, galaxy role, assurance level, and control identifier.

```bash
python tools/generate_cyfun_2023.py \
  --pdf-dir /path/to/official-cyfun-pdfs \
  --output-dir . \
  --validate /path/to/misp-galaxy-schema-files
```

The package has been validated against the official MISP `schema_clusters.json` and `schema_galaxies.json` schemas from the `MISP/misp-galaxy` repository.

## Source documents

The official CCB framework landing page and the four official PDFs are referenced directly in the cluster metadata (`meta.refs`) and cluster `source` fields.
