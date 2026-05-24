# Validation report - CyberFundamentals 2023 MISP Galaxy

Generated package validation summary.

## Coverage checks

| Item | Count |
| --- | ---: |
| Small level-specific values | 7 |
| Basic level-specific values | 33 |
| Important level-specific values | 93 |
| Essential level-specific values | 100 |
| Assurance matrix values | 233 |
| Normalized catalogue values | 107 |
| Broken catalogue relations | 0 |

## Key-measure controls represented by assurance scope

| Assurance level | Controls marked in scope |
| --- | ---: |
| Basic | 9 |
| Important (including inherited Basic list) | 14 |
| Essential (including inherited Basic and Important lists) | 18 |

## Validation performed

- Parsed the four official CCB PDF files and verified the page/control extraction counts.
- Rendered representative PDF source pages for visual inspection of table-of-contents, control and annex layouts.
- Confirmed unique UUIDs and unique values in each generated cluster.
- Confirmed every assurance-instance relationship resolves to a normalized catalogue UUID.
- Validated all generated galaxy and cluster JSON files against the official MISP `schema_galaxies.json` and `schema_clusters.json` definitions.
- Parsed all generated JSON files with Python's JSON parser.

## Generated JSON SHA-256

- `clusters/cyfun-assurance-requirements-2023.json`: `8557993afdfb1410156e65e97e83643c9f544d811406e4b812a8b129c35b7775`
- `clusters/cyfun-control-catalogue-2023.json`: `91b3c9ddfc4013241624b40c14ac7857d2b988b5901a3b9fe33f84415228480c`
- `galaxies/cyfun-assurance-requirements-2023.json`: `04d9269e40fc3a186e783bbf4637cdb84450ded0533235599876c62771b5bf52`
- `galaxies/cyfun-control-catalogue-2023.json`: `23785ac47564aa1626383fb17e0af8e31c70fd9dba42789c7aba79dc6598d7d5`

## Source PDF SHA-256 (not distributed in this package)

- `CyFun2023-BASIC.pdf`: `fca8c36d46501862cf017fce5bae0115f723c9edf9d3405debf70c3252706e61`
- `CyFun2023-ESSENTIAL.pdf`: `4c5b91584907b3dca63ad4287b0f6ccf8373967e9494207c9bcf7f1b11c0ed32`
- `CyFun2023-IMPORTANT.pdf`: `d5794728c138b6512043879bcd80cbe6bf77e7022d7666c8357fbe190b312b49`
- `CyFun2023-SMALL.pdf`: `e8a7acc34a59012d2c64c29b09a4b48066ec0187921cb09d2fe523ea4c1a7537`
