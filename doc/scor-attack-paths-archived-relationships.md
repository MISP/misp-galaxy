# scor-attack-paths: archived precalculated relationships
The refined SCOR approach prohibits cluster files from shipping precalculated `related[]` arrays. Relationships among clusters are built by analysts in MISP at investigation time. The four historical scor-attack-paths entries (Viasat KA-SAT AcidRain, Gatwick UAS Incursions, Fengyun-1C ASAT, Yacht GPS Spoofing PoC) previously carried `related[]` data; those assertions are archived here so the analyst guidance is preserved.

## Viasat KA-SAT AcidRain (2022)
- Cluster value UUID: `7e1c4a8b-3d5f-4e2a-9c8b-000000000001`

Previously-shipped relationships:

| Type | Target UUID | Tags |
| --- | --- | --- |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-100000000001` | `scor-eten:"PCE:TE:Terrestrial:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-100000000004` | `scor-eten:"PCE:OR:Orbital:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-200000000003` | `scor-eten:"SEG:GR:Ground:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-200000000002` | `scor-eten:"SEG:LI:Link:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-200000000004` | `scor-eten:"SEG:US:User:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-200000000009` | `scor-eten:"SEG:SP:Space:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-300000000001` | `scor-eten:"SVC:CP:Control Plane:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-300000000002` | `scor-eten:"SVC:DP:Data Plane:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-400000000003` | `scor-eten:"AST:SW:Software:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-400000000002` | `scor-eten:"AST:FW:Firmware:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-400000000001` | `scor-eten:"AST:HW:Hardware:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-400000000005` | `scor-eten:"AST:SI:Signal:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-400000000004` | `scor-eten:"AST:DA:Data:00"` |
| instance-of | `7e1c4a8b-3d5f-4e2a-9c8b-500000000003` | `scor-eten:"AN:ATT:Attack Path:00"` |

## Gatwick UAS Incursions (2018)
- Cluster value UUID: `7e1c4a8b-3d5f-4e2a-9c8b-000000000002`

Previously-shipped relationships:

| Type | Target UUID | Tags |
| --- | --- | --- |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-100000000003` | `scor-eten:"PCE:AE:Aerial:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-100000000001` | `scor-eten:"PCE:TE:Terrestrial:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-200000000006` | `scor-eten:"SEG:LO:Low Altitude:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-200000000003` | `scor-eten:"SEG:GR:Ground:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-300000000001` | `scor-eten:"SVC:CP:Control Plane:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-400000000001` | `scor-eten:"AST:HW:Hardware:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-400000000005` | `scor-eten:"AST:SI:Signal:00"` |
| instance-of | `7e1c4a8b-3d5f-4e2a-9c8b-500000000003` | `scor-eten:"AN:ATT:Attack Path:00"` |

## Fengyun-1C Chinese ASAT Test (2007)
- Cluster value UUID: `7e1c4a8b-3d5f-4e2a-9c8b-000000000003`

Previously-shipped relationships:

| Type | Target UUID | Tags |
| --- | --- | --- |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-100000000004` | `scor-eten:"PCE:OR:Orbital:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-200000000009` | `scor-eten:"SEG:SP:Space:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-300000000002` | `scor-eten:"SVC:DP:Data Plane:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-400000000001` | `scor-eten:"AST:HW:Hardware:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-400000000004` | `scor-eten:"AST:DA:Data:00"` |
| instance-of | `7e1c4a8b-3d5f-4e2a-9c8b-500000000003` | `scor-eten:"AN:ATT:Attack Path:00"` |

## Yacht GPS Spoofing PoC (UT Austin, 2013)
- Cluster value UUID: `7e1c4a8b-3d5f-4e2a-9c8b-000000000004`

Previously-shipped relationships:

| Type | Target UUID | Tags |
| --- | --- | --- |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-100000000002` | `scor-eten:"PCE:AQ:Aquatic:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-200000000005` | `scor-eten:"SEG:AQ:Aquatic:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-300000000001` | `scor-eten:"SVC:CP:Control Plane:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-400000000005` | `scor-eten:"AST:SI:Signal:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-400000000001` | `scor-eten:"AST:HW:Hardware:00"` |
| TOE | `7e1c4a8b-3d5f-4e2a-9c8b-400000000004` | `scor-eten:"AST:DA:Data:00"` |
| instance-of | `7e1c4a8b-3d5f-4e2a-9c8b-500000000003` | `scor-eten:"AN:ATT:Attack Path:00"` |

