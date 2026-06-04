# PLOT4ai galaxy generator

This directory contains the generator for the PLOT4ai MISP galaxy.

## Usage

From the repository root:

```bash
python tools/plot4ai/generate_plot4ai_galaxy.py --output-dir . --validate
```

By default, the generator downloads the upstream PLOT4ai deck from
`https://raw.githubusercontent.com/PLOT4ai/plot4ai-library/main/deck.json`.
For reproducible offline generation, pass a local deck file:

```bash
python tools/plot4ai/generate_plot4ai_galaxy.py --source /path/to/deck.json --output-dir . --validate
```

The generated files are:

- `galaxies/plot4ai.json`
- `clusters/plot4ai.json`

The generator preserves PLOT4ai card metadata such as AI types, roles, phases,
categories, threat condition, questions, recommendations, CIA values when
available, references, source names, source text, license, and source provenance.
It also adds conservative relationships to existing MISP galaxies where a close
mapping exists, primarily MITRE ATLAS and Agent Threat Rules.
