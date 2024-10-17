# misp-galaxy

![Python application](https://github.com/MISP/misp-galaxy/workflows/Python%20application/badge.svg)

![Screenshot - MISP galaxy integeration in MISP threat intelligence platform](https://raw.githubusercontent.com/MISP/misp-galaxy/aa41337fd78946a60aef3783f58f337d2342430a/doc/images/galaxy.png)

MISP galaxy is a simple method to express a large object called cluster that can be attached to MISP events or
attributes. A cluster can be composed of one or more elements. Elements are expressed as key-values. There
are default knowledge base (such as Threat Actors, Tools, Ransomware, ATT&CK matrixes) available in MISP galaxy
but those can be overwritten, replaced, updated, forked and shared as you wish.

Existing clusters and vocabularies can be used as-is or as a common knowledge base. MISP distribution can be applied
to each cluster to permit a limited or broader distribution scheme.

Galaxies can be also used to expressed existing matrix-like standards such as MITRE ATT&CK(tm) or custom ones.

The objective is to have a comment set of clusters for organizations starting analysis but that can be expanded
to localized information (which is not shared) or additional information (that can be shared).

# Available Galaxy - clusters

## 360.net Threat Actors

[360.net Threat Actors](https://www.misp-galaxy.org/360net) - Known or estimated adversary groups as identified by 360.net.

Category: *actor* - source: *https://apt.360.net/aptlist* - total: *42* elements

[[HTML](https://www.misp-galaxy.org/360net)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/360net.json)]

## Ammunitions

[Ammunitions](https://www.misp-galaxy.org/ammunitions) - Common ammunitions galaxy

Category: *firearm* - source: *https://ammo.com/* - total: *409* elements

[[HTML](https://www.misp-galaxy.org/ammunitions)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/ammunitions.json)]

## Android

[Android](https://www.misp-galaxy.org/android) - Android malware galaxy based on multiple open sources.

Category: *tool* - source: *Open Sources* - total: *433* elements

[[HTML](https://www.misp-galaxy.org/android)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/android.json)]

## Azure Threat Research Matrix

[Azure Threat Research Matrix](https://www.misp-galaxy.org/atrm) - The purpose of the Azure Threat Research Matrix (ATRM) is to educate readers on the potential of Azure-based tactics, techniques, and procedures (TTPs). It is not to teach how to weaponize or specifically abuse them. For this reason, some specific commands will be obfuscated or parts will be omitted to prevent abuse.

Category: *atrm* - source: *https://github.com/microsoft/Azure-Threat-Research-Matrix* - total: *90* elements

[[HTML](https://www.misp-galaxy.org/atrm)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/atrm.json)]

## attck4fraud

[attck4fraud](https://www.misp-galaxy.org/attck4fraud) - attck4fraud - Principles of MITRE ATT&CK in the fraud domain

Category: *guidelines* - source: *Open Sources* - total: *71* elements

[[HTML](https://www.misp-galaxy.org/attck4fraud)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/attck4fraud.json)]

## Backdoor

[Backdoor](https://www.misp-galaxy.org/backdoor) - A list of backdoor malware.

Category: *tool* - source: *Open Sources* - total: *29* elements

[[HTML](https://www.misp-galaxy.org/backdoor)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/backdoor.json)]

## Banker

[Banker](https://www.misp-galaxy.org/banker) - A list of banker malware.

Category: *tool* - source: *Open Sources* - total: *53* elements

[[HTML](https://www.misp-galaxy.org/banker)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/banker.json)]

## Bhadra Framework

[Bhadra Framework](https://www.misp-galaxy.org/bhadra-framework) - Bhadra Threat Modeling Framework

Category: *mobile* - source: *https://arxiv.org/pdf/2005.05110.pdf* - total: *47* elements

[[HTML](https://www.misp-galaxy.org/bhadra-framework)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/bhadra-framework.json)]

## Botnet

[Botnet](https://www.misp-galaxy.org/botnet) - botnet galaxy

Category: *tool* - source: *MISP Project* - total: *132* elements

[[HTML](https://www.misp-galaxy.org/botnet)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/botnet.json)]

## Branded Vulnerability

[Branded Vulnerability](https://www.misp-galaxy.org/branded_vulnerability) - List of known vulnerabilities and attacks with a branding

Category: *vulnerability* - source: *Open Sources* - total: *14* elements

[[HTML](https://www.misp-galaxy.org/branded_vulnerability)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/branded_vulnerability.json)]

## Cert EU GovSector

[Cert EU GovSector](https://www.misp-galaxy.org/cert-eu-govsector) - Cert EU GovSector

Category: *sector* - source: *CERT-EU* - total: *6* elements

[[HTML](https://www.misp-galaxy.org/cert-eu-govsector)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/cert-eu-govsector.json)]

## China Defence Universities Tracker

[China Defence Universities Tracker](https://www.misp-galaxy.org/china-defence-universities) - The China Defence Universities Tracker is a database of Chinese institutions engaged in military or security-related science and technology research. It was created by ASPI’s International Cyber Policy Centre.

Category: *academic-institution* - source: *ASPI International Cyber Policy Centre* - total: *159* elements

[[HTML](https://www.misp-galaxy.org/china-defence-universities)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/china-defence-universities.json)]

## CONCORDIA Mobile Modelling Framework - Attack Pattern

[CONCORDIA Mobile Modelling Framework - Attack Pattern](https://www.misp-galaxy.org/cmtmf-attack-pattern) - A list of Techniques in CONCORDIA Mobile Modelling Framework.

Category: *cmtmf-attack-pattern* - source: *https://5g4iot.vlab.cs.hioa.no/* - total: *93* elements

[[HTML](https://www.misp-galaxy.org/cmtmf-attack-pattern)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/cmtmf-attack-pattern.json)]

## Country

[Country](https://www.misp-galaxy.org/country) - Country meta information based on the database provided by geonames.org.

Category: *country* - source: *MISP Project* - total: *252* elements

[[HTML](https://www.misp-galaxy.org/country)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/country.json)]

## Cryptominers

[Cryptominers](https://www.misp-galaxy.org/cryptominers) - A list of cryptominer and cryptojacker malware.

Category: *Cryptominers* - source: *Open Source Intelligence* - total: *5* elements

[[HTML](https://www.misp-galaxy.org/cryptominers)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/cryptominers.json)]

## Actor Types

[Actor Types](https://www.misp-galaxy.org/disarm-actortypes) - DISARM is a framework designed for describing and understanding disinformation incidents.

Category: *disarm* - source: *https://github.com/DISARMFoundation/DISARMframeworks* - total: *33* elements

[[HTML](https://www.misp-galaxy.org/disarm-actortypes)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/disarm-actortypes.json)]

## Countermeasures

[Countermeasures](https://www.misp-galaxy.org/disarm-countermeasures) - DISARM is a framework designed for describing and understanding disinformation incidents.

Category: *disarm* - source: *https://github.com/DISARMFoundation/DISARMframeworks* - total: *139* elements

[[HTML](https://www.misp-galaxy.org/disarm-countermeasures)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/disarm-countermeasures.json)]

## Detections

[Detections](https://www.misp-galaxy.org/disarm-detections) - DISARM is a framework designed for describing and understanding disinformation incidents.

Category: *disarm* - source: *https://github.com/DISARMFoundation/DISARMframeworks* - total: *94* elements

[[HTML](https://www.misp-galaxy.org/disarm-detections)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/disarm-detections.json)]

## Techniques

[Techniques](https://www.misp-galaxy.org/disarm-techniques) - DISARM is a framework designed for describing and understanding disinformation incidents.

Category: *disarm* - source: *https://github.com/DISARMFoundation/DISARMframeworks* - total: *298* elements

[[HTML](https://www.misp-galaxy.org/disarm-techniques)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/disarm-techniques.json)]

## Election guidelines

[Election guidelines](https://www.misp-galaxy.org/election-guidelines) - Universal Development and Security Guidelines as Applicable to Election Technology.

Category: *guidelines* - source: *Open Sources* - total: *23* elements

[[HTML](https://www.misp-galaxy.org/election-guidelines)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/election-guidelines.json)]

## Entity

[Entity](https://www.misp-galaxy.org/entity) - Description of entities that can be involved in events.

Category: *actor* - source: *MISP Project* - total: *4* elements

[[HTML](https://www.misp-galaxy.org/entity)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/entity.json)]

## Exploit-Kit

[Exploit-Kit](https://www.misp-galaxy.org/exploit-kit) - Exploit-Kit is an enumeration of some exploitation kits used by adversaries. The list includes document, browser and router exploit kits.It's not meant to be totally exhaustive but aim at covering the most seen in the past 5 years

Category: *tool* - source: *MISP Project* - total: *52* elements

[[HTML](https://www.misp-galaxy.org/exploit-kit)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/exploit-kit.json)]

## Firearms

[Firearms](https://www.misp-galaxy.org/firearms) - Common firearms galaxy

Category: *firearm* - source: *https://www.impactguns.com* - total: *5953* elements

[[HTML](https://www.misp-galaxy.org/firearms)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/firearms.json)]

## FIRST CSIRT Services Framework

[FIRST CSIRT Services Framework](https://www.misp-galaxy.org/first-csirt-services-framework) - The Computer Security Incident Response Team (CSIRT) Services Framework is a high-level document describing in a structured way a collection of cyber security services and associated functions that Computer Security Incident Response Teams and other teams providing incident management related services may provide

Category: *csirt* - source: *https://www.first.org/standards/frameworks/csirts/csirt_services_framework_v2.1* - total: *97* elements

[[HTML](https://www.misp-galaxy.org/first-csirt-services-framework)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/first-csirt-services-framework.json)]

## FIRST DNS Abuse Techniques Matrix

[FIRST DNS Abuse Techniques Matrix](https://www.misp-galaxy.org/first-dns) - The Domain Name System (DNS) is a critical part of the Internet, including mapping domain names to IP addresses. Malicious threat actors use domain names, their corresponding technical resources, and other parts of the DNS infrastructure, including its protocols, for their malicious cyber operations. CERTs are confronted with reported DNS abuse on a continuous basis, and rely heavily on DNS analysis and infrastructure to protect their constituencies. Understanding the international customary norms applicable for detecting and mitigating DNS abuse from the perspective of the global incident response community is critical for the open Internet’s stability, security and resiliency. See also https://www.first.org/global/sigs/dns/ for more information.

Category: *first-dns* - source: *https://www.first.org/global/sigs/dns/* - total: *21* elements

[[HTML](https://www.misp-galaxy.org/first-dns)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/first-dns.json)]

## GSMA MoTIF

[GSMA MoTIF](https://www.misp-galaxy.org/gsma-motif) - Mobile Threat Intelligence Framework (MoTIF) Principles. 

Category: *attack-pattern* - source: *https://www.gsma.com/solutions-and-impact/technologies/security/latest-news/establishing-motif-the-mobile-threat-intelligence-framework/* - total: *50* elements

[[HTML](https://www.misp-galaxy.org/gsma-motif)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/gsma-motif.json)]

## Intelligence Agencies

[Intelligence Agencies](https://www.misp-galaxy.org/intelligence-agencies) - List of intelligence agencies

Category: *Intelligence Agencies* - source: *https://en.wikipedia.org/wiki/List_of_intelligence_agencies* - total: *436* elements

[[HTML](https://www.misp-galaxy.org/intelligence-agencies)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/intelligence-agencies.json)]

## INTERPOL DWVA Taxonomy

[INTERPOL DWVA Taxonomy](https://www.misp-galaxy.org/interpol-dwva) - This taxonomy defines common forms of abuses and entities that represent real-world actors and service that are part of a larger Darknet- and Cryptoasset Ecosystems.

Category: *dwva* - source: *https://interpol-innovation-centre.github.io/DW-VA-Taxonomy/* - total: *94* elements

[[HTML](https://www.misp-galaxy.org/interpol-dwva)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/interpol-dwva.json)]

## Malpedia

[Malpedia](https://www.misp-galaxy.org/malpedia) - Malware galaxy cluster based on Malpedia.

Category: *tool* - source: *Malpedia* - total: *3038* elements

[[HTML](https://www.misp-galaxy.org/malpedia)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/malpedia.json)]

## Microsoft Activity Group actor

[Microsoft Activity Group actor](https://www.misp-galaxy.org/microsoft-activity-group) - Activity groups as described by Microsoft

Category: *actor* - source: *MISP Project* - total: *79* elements

[[HTML](https://www.misp-galaxy.org/microsoft-activity-group)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/microsoft-activity-group.json)]

## Misinformation Pattern

[Misinformation Pattern](https://www.misp-galaxy.org/misinfosec-amitt-misinformation-pattern) - AM!TT Technique

Category: *misinformation-pattern* - source: *https://github.com/misinfosecproject/amitt_framework* - total: *61* elements

[[HTML](https://www.misp-galaxy.org/misinfosec-amitt-misinformation-pattern)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/misinfosec-amitt-misinformation-pattern.json)]

## MITRE ATLAS Attack Pattern

[MITRE ATLAS Attack Pattern](https://www.misp-galaxy.org/mitre-atlas-attack-pattern) - MITRE ATLAS Attack Pattern - Adversarial Threat Landscape for Artificial-Intelligence Systems

Category: *attack-pattern* - source: *https://github.com/mitre-atlas/atlas-navigator-data* - total: *82* elements

[[HTML](https://www.misp-galaxy.org/mitre-atlas-attack-pattern)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-atlas-attack-pattern.json)]

## MITRE ATLAS Course of Action

[MITRE ATLAS Course of Action](https://www.misp-galaxy.org/mitre-atlas-course-of-action) - MITRE ATLAS Mitigation - Adversarial Threat Landscape for Artificial-Intelligence Systems

Category: *course-of-action* - source: *https://github.com/mitre-atlas/atlas-navigator-data* - total: *20* elements

[[HTML](https://www.misp-galaxy.org/mitre-atlas-course-of-action)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-atlas-course-of-action.json)]

## Attack Pattern

[Attack Pattern](https://www.misp-galaxy.org/mitre-attack-pattern) - ATT&CK tactic

Category: *attack-pattern* - source: *https://github.com/mitre/cti* - total: *1141* elements

[[HTML](https://www.misp-galaxy.org/mitre-attack-pattern)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-attack-pattern.json)]

## Course of Action

[Course of Action](https://www.misp-galaxy.org/mitre-course-of-action) - ATT&CK Mitigation

Category: *course-of-action* - source: *https://github.com/mitre/cti* - total: *281* elements

[[HTML](https://www.misp-galaxy.org/mitre-course-of-action)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-course-of-action.json)]

## MITRE D3FEND

[MITRE D3FEND](https://www.misp-galaxy.org/mitre-d3fend) - A knowledge graph of cybersecurity countermeasures.

Category: *d3fend* - source: *https://d3fend.mitre.org/* - total: *171* elements

[[HTML](https://www.misp-galaxy.org/mitre-d3fend)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-d3fend.json)]

## mitre-data-component

[mitre-data-component](https://www.misp-galaxy.org/mitre-data-component) - Data components are parts of data sources. 

Category: *data-component* - source: *https://github.com/mitre/cti* - total: *117* elements

[[HTML](https://www.misp-galaxy.org/mitre-data-component)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-data-component.json)]

## mitre-data-source

[mitre-data-source](https://www.misp-galaxy.org/mitre-data-source) - Data sources represent the various subjects/topics of information that can be collected by sensors/logs. 

Category: *data-source* - source: *https://github.com/mitre/cti* - total: *40* elements

[[HTML](https://www.misp-galaxy.org/mitre-data-source)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-data-source.json)]

## Assets

[Assets](https://www.misp-galaxy.org/mitre-ics-assets) - A list of asset categories that are commonly found in industrial control systems.

Category: *asset* - source: *https://collaborate.mitre.org/attackics/index.php/All_Assets* - total: *7* elements

[[HTML](https://www.misp-galaxy.org/mitre-ics-assets)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-ics-assets.json)]

## Groups

[Groups](https://www.misp-galaxy.org/mitre-ics-groups) - Groups are sets of related intrusion activity that are tracked by a common name in the security community. Groups are also sometimes referred to as campaigns or intrusion sets. Some groups have multiple names associated with the same set of activities due to various organizations tracking the same set of activities by different names. Groups are mapped to publicly reported technique use and referenced in the ATT&CK for ICS knowledge base. Groups are also mapped to reported software used during intrusions.

Category: *actor* - source: *https://collaborate.mitre.org/attackics/index.php/Groups* - total: *10* elements

[[HTML](https://www.misp-galaxy.org/mitre-ics-groups)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-ics-groups.json)]

## Levels

[Levels](https://www.misp-galaxy.org/mitre-ics-levels) - Based on the Purdue Model to aid ATT&CK for ICS users to understand which techniques are applicable to their environment.

Category: *level* - source: *https://collaborate.mitre.org/attackics/index.php/All_Levels* - total: *3* elements

[[HTML](https://www.misp-galaxy.org/mitre-ics-levels)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-ics-levels.json)]

## Software

[Software](https://www.misp-galaxy.org/mitre-ics-software) - Software is a generic term for custom or commercial code, operating system utilities, open-source software, or other tools used to conduct behavior modeled in ATT&CK for ICS.

Category: *tool* - source: *https://collaborate.mitre.org/attackics/index.php/Software* - total: *17* elements

[[HTML](https://www.misp-galaxy.org/mitre-ics-software)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-ics-software.json)]

## Tactics

[Tactics](https://www.misp-galaxy.org/mitre-ics-tactics) - A list of all 11 tactics in ATT&CK for ICS

Category: *tactic* - source: *https://collaborate.mitre.org/attackics/index.php/All_Tactics* - total: *9* elements

[[HTML](https://www.misp-galaxy.org/mitre-ics-tactics)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-ics-tactics.json)]

## Techniques

[Techniques](https://www.misp-galaxy.org/mitre-ics-techniques) - A list of Techniques in ATT&CK for ICS.

Category: *attack-pattern* - source: *https://collaborate.mitre.org/attackics/index.php/All_Techniques* - total: *78* elements

[[HTML](https://www.misp-galaxy.org/mitre-ics-techniques)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-ics-techniques.json)]

## Intrusion Set

[Intrusion Set](https://www.misp-galaxy.org/mitre-intrusion-set) - Name of ATT&CK Group

Category: *actor* - source: *https://github.com/mitre/cti* - total: *165* elements

[[HTML](https://www.misp-galaxy.org/mitre-intrusion-set)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-intrusion-set.json)]

## Malware

[Malware](https://www.misp-galaxy.org/mitre-malware) - Name of ATT&CK software

Category: *tool* - source: *https://github.com/mitre/cti* - total: *705* elements

[[HTML](https://www.misp-galaxy.org/mitre-malware)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-malware.json)]

## mitre-tool

[mitre-tool](https://www.misp-galaxy.org/mitre-tool) - Name of ATT&CK software

Category: *tool* - source: *https://github.com/mitre/cti* - total: *87* elements

[[HTML](https://www.misp-galaxy.org/mitre-tool)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-tool.json)]

## NACE

[NACE](https://www.misp-galaxy.org/nace) - version 2.1 - The Statistical Classification of Economic Activities in the European Community, commonly referred to as NACE (for the French term "nomenclature statistique des activités économiques dans la Communauté européenne"), is the industry standard classification system used in the European Union.

Category: *sector* - source: *https://ec.europa.eu/eurostat/web/metadata/classifications* - total: *1047* elements

[[HTML](https://www.misp-galaxy.org/nace)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/nace.json)]

## NAICS

[NAICS](https://www.misp-galaxy.org/naics) - The North American Industry Classification System or NAICS is a classification of business establishments by type of economic activity (the process of production).

Category: *sector* - source: *North American Industry Classification System - NAICS* - total: *2125* elements

[[HTML](https://www.misp-galaxy.org/naics)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/naics.json)]

## NICE Competency areas

[NICE Competency areas](https://www.misp-galaxy.org/nice-framework-competency_areas) - Competency areas based on the NIST NICE framework

Category: *workforce* - source: *https://csrc.nist.gov/pubs/sp/800/181/r1/final* - total: *11* elements

[[HTML](https://www.misp-galaxy.org/nice-framework-competency_areas)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/nice-framework-competency_areas.json)]

## NICE Knowledges

[NICE Knowledges](https://www.misp-galaxy.org/nice-framework-knowledges) - Knowledge based on the NIST NICE framework

Category: *workforce* - source: *https://csrc.nist.gov/pubs/sp/800/181/r1/final* - total: *640* elements

[[HTML](https://www.misp-galaxy.org/nice-framework-knowledges)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/nice-framework-knowledges.json)]

## OPM codes in cybersecurity

[OPM codes in cybersecurity](https://www.misp-galaxy.org/nice-framework-opm_codes) - Office of Personnel Management codes in cybersecurity

Category: *workforce* - source: *https://dw.opm.gov/datastandards/referenceData/2273/current* - total: *52* elements

[[HTML](https://www.misp-galaxy.org/nice-framework-opm_codes)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/nice-framework-opm_codes.json)]

## NICE Skills

[NICE Skills](https://www.misp-galaxy.org/nice-framework-skills) - Skills based on the NIST NICE framework

Category: *workforce* - source: *https://csrc.nist.gov/pubs/sp/800/181/r1/final* - total: *556* elements

[[HTML](https://www.misp-galaxy.org/nice-framework-skills)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/nice-framework-skills.json)]

## NICE Tasks

[NICE Tasks](https://www.misp-galaxy.org/nice-framework-tasks) - Tasks based on the NIST NICE framework

Category: *workforce* - source: *https://csrc.nist.gov/pubs/sp/800/181/r1/final* - total: *1084* elements

[[HTML](https://www.misp-galaxy.org/nice-framework-tasks)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/nice-framework-tasks.json)]

## NICE Work Roles

[NICE Work Roles](https://www.misp-galaxy.org/nice-framework-work_roles) - Work roles based on the NIST NICE framework

Category: *workforce* - source: *https://csrc.nist.gov/pubs/sp/800/181/r1/final* - total: *52* elements

[[HTML](https://www.misp-galaxy.org/nice-framework-work_roles)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/nice-framework-work_roles.json)]

## o365-exchange-techniques

[o365-exchange-techniques](https://www.misp-galaxy.org/o365-exchange-techniques) - o365-exchange-techniques - Office365/Exchange related techniques by @johnLaTwC and @inversecos

Category: *guidelines* - source: *Open Sources, https://www.inversecos.com/2021/09/office365-attacks-bypassing-mfa.html* - total: *62* elements

[[HTML](https://www.misp-galaxy.org/o365-exchange-techniques)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/o365-exchange-techniques.json)]

## online-service

[online-service](https://www.misp-galaxy.org/online-service) - Known public online services.

Category: *tool* - source: *Open Sources* - total: *1* elements

[[HTML](https://www.misp-galaxy.org/online-service)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/online-service.json)]

## Preventive Measure

[Preventive Measure](https://www.misp-galaxy.org/preventive-measure) - Preventive measures based on the ransomware document overview as published in https://docs.google.com/spreadsheets/d/1TWS238xacAto-fLKh1n5uTsdijWdCEsGIM0Y0Hvmc5g/pubhtml# . The preventive measures are quite generic and can fit any standard Windows infrastructure and their security measures.

Category: *measure* - source: *MISP Project* - total: *20* elements

[[HTML](https://www.misp-galaxy.org/preventive-measure)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/preventive-measure.json)]

## Producer

[Producer](https://www.misp-galaxy.org/producer) - List of threat intelligence producer from security vendors to CERTs including any producer of intelligence at large.

Category: *actor* - source: *MISP Project* - total: *46* elements

[[HTML](https://www.misp-galaxy.org/producer)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/producer.json)]

## Ransomware

[Ransomware](https://www.misp-galaxy.org/ransomware) - Ransomware galaxy based on different sources and maintained by the MISP Project.

Category: *tool* - source: *Various* - total: *1809* elements

[[HTML](https://www.misp-galaxy.org/ransomware)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/ransomware.json)]

## RAT

[RAT](https://www.misp-galaxy.org/rat) - remote administration tool or remote access tool (RAT), also called sometimes remote access trojan, is a piece of software or programming that allows a remote "operator" to control a system as if they have physical access to that system.

Category: *tool* - source: *MISP Project* - total: *265* elements

[[HTML](https://www.misp-galaxy.org/rat)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/rat.json)]

## Regions UN M49

[Regions UN M49](https://www.misp-galaxy.org/region) - Regions based on UN M49.

Category: *location* - source: *https://unstats.un.org/unsd/methodology/m49/overview/* - total: *32* elements

[[HTML](https://www.misp-galaxy.org/region)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/region.json)]

## rsit

[rsit](https://www.misp-galaxy.org/rsit) - rsit

Category: *rsit* - source: *https://github.com/enisaeu/Reference-Security-Incident-Taxonomy-Task-Force* - total: *39* elements

[[HTML](https://www.misp-galaxy.org/rsit)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/rsit.json)]

## Sector

[Sector](https://www.misp-galaxy.org/sector) - Activity sectors

Category: *sector* - source: *CERT-EU* - total: *118* elements

[[HTML](https://www.misp-galaxy.org/sector)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/sector.json)]

## Sigma-Rules

[Sigma-Rules](https://www.misp-galaxy.org/sigma-rules) - MISP galaxy cluster based on Sigma Rules.

Category: *rules* - source: *https://github.com/jstnk9/MISP/tree/main/misp-galaxy/sigma* - total: *2970* elements

[[HTML](https://www.misp-galaxy.org/sigma-rules)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/sigma-rules.json)]

## Dark Patterns

[Dark Patterns](https://www.misp-galaxy.org/social-dark-patterns) - Dark Patterns are user interface that tricks users into making decisions that benefit the interface's holder to the expense of the user.

Category: *dark-patterns* - source: *CIRCL* - total: *19* elements

[[HTML](https://www.misp-galaxy.org/social-dark-patterns)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/social-dark-patterns.json)]

## SoD Matrix

[SoD Matrix](https://www.misp-galaxy.org/sod-matrix) - SOD Matrix

Category: *sod-matrix* - source: *https://github.com/cudeso/SoD-Matrix* - total: *276* elements

[[HTML](https://www.misp-galaxy.org/sod-matrix)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/sod-matrix.json)]

## Stealer

[Stealer](https://www.misp-galaxy.org/stealer) - A list of malware stealer.

Category: *tool* - source: *Open Sources* - total: *16* elements

[[HTML](https://www.misp-galaxy.org/stealer)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/stealer.json)]

## Surveillance Vendor

[Surveillance Vendor](https://www.misp-galaxy.org/surveillance-vendor) - List of vendors selling surveillance technologies including malware, interception devices or computer exploitation services.

Category: *actor* - source: *MISP Project* - total: *50* elements

[[HTML](https://www.misp-galaxy.org/surveillance-vendor)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/surveillance-vendor.json)]

## Target Information

[Target Information](https://www.misp-galaxy.org/target-information) - Description of targets of threat actors.

Category: *target* - source: *Various* - total: *241* elements

[[HTML](https://www.misp-galaxy.org/target-information)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/target-information.json)]

## TDS

[TDS](https://www.misp-galaxy.org/tds) - TDS is a list of Traffic Direction System used by adversaries

Category: *tool* - source: *MISP Project* - total: *11* elements

[[HTML](https://www.misp-galaxy.org/tds)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/tds.json)]

## Tea Matrix

[Tea Matrix](https://www.misp-galaxy.org/tea-matrix) - Tea Matrix

Category: *tea-matrix* - source: ** - total: *7* elements

[[HTML](https://www.misp-galaxy.org/tea-matrix)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/tea-matrix.json)]

## Threat Actor

[Threat Actor](https://www.misp-galaxy.org/threat-actor) - Known or estimated adversary groups targeting organizations and employees. Adversary groups are regularly confused with their initial operation or campaign. threat-actor-classification meta can be used to clarify the understanding of the threat-actor if also considered as operation, campaign or activity group.

Category: *actor* - source: *MISP Project* - total: *751* elements

[[HTML](https://www.misp-galaxy.org/threat-actor)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/threat-actor.json)]

## Tidal Campaigns

[Tidal Campaigns](https://www.misp-galaxy.org/tidal-campaigns) - Tidal Campaigns Cluster

Category: *Campaigns* - source: *https://app-api.tidalcyber.com/api/v1/campaigns/* - total: *83* elements

[[HTML](https://www.misp-galaxy.org/tidal-campaigns)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/tidal-campaigns.json)]

## Tidal Groups

[Tidal Groups](https://www.misp-galaxy.org/tidal-groups) - Tidal Groups Galaxy

Category: *Threat Groups* - source: *https://app-api.tidalcyber.com/api/v1/groups/* - total: *206* elements

[[HTML](https://www.misp-galaxy.org/tidal-groups)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/tidal-groups.json)]

## Tidal References

[Tidal References](https://www.misp-galaxy.org/tidal-references) - Tidal References Cluster

Category: *References* - source: *https://app-api.tidalcyber.com/api/v1/references/* - total: *4349* elements

[[HTML](https://www.misp-galaxy.org/tidal-references)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/tidal-references.json)]

## Tidal Software

[Tidal Software](https://www.misp-galaxy.org/tidal-software) - Tidal Software Cluster

Category: *Software* - source: *https://app-api.tidalcyber.com/api/v1/software/* - total: *1053* elements

[[HTML](https://www.misp-galaxy.org/tidal-software)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/tidal-software.json)]

## Tidal Tactic

[Tidal Tactic](https://www.misp-galaxy.org/tidal-tactic) - Tidal Tactic Cluster

Category: *Tactic* - source: *https://app-api.tidalcyber.com/api/v1/tactic/* - total: *14* elements

[[HTML](https://www.misp-galaxy.org/tidal-tactic)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/tidal-tactic.json)]

## Tidal Technique

[Tidal Technique](https://www.misp-galaxy.org/tidal-technique) - Tidal Technique Cluster

Category: *Technique* - source: *https://app-api.tidalcyber.com/api/v1/technique/* - total: *202* elements

[[HTML](https://www.misp-galaxy.org/tidal-technique)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/tidal-technique.json)]

## Threat Matrix for storage services

[Threat Matrix for storage services](https://www.misp-galaxy.org/tmss) - Microsoft Defender for Cloud threat matrix for storage services contains attack tactics, techniques and mitigations relevant storage services delivered by cloud providers.

Category: *tmss* - source: *https://github.com/microsoft/Threat-matrix-for-storage-services* - total: *40* elements

[[HTML](https://www.misp-galaxy.org/tmss)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/tmss.json)]

## Tool

[Tool](https://www.misp-galaxy.org/tool) - threat-actor-tools is an enumeration of tools used by adversaries. The list includes malware but also common software regularly used by the adversaries.

Category: *tool* - source: *MISP Project* - total: *603* elements

[[HTML](https://www.misp-galaxy.org/tool)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/tool.json)]

## UAVs/UCAVs

[UAVs/UCAVs](https://www.misp-galaxy.org/uavs) - Unmanned Aerial Vehicles / Unmanned Combat Aerial Vehicles

Category: *military equipment* - source: *Popular Mechanics* - total: *36* elements

[[HTML](https://www.misp-galaxy.org/uavs)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/uavs.json)]

## UKHSA Culture Collections

[UKHSA Culture Collections](https://www.misp-galaxy.org/ukhsa-culture-collections) - UK Health Security Agency Culture Collections represent deposits of cultures that consist of expertly preserved, authenticated cell lines and microbial strains of known provenance.

Category: *virus* - source: *https://www.culturecollections.org.uk* - total: *6638* elements

[[HTML](https://www.misp-galaxy.org/ukhsa-culture-collections)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/ukhsa-culture-collections.json)]


# Online documentation

The [misp-galaxy.org](https://misp-galaxy.org) website provides an easily navigable resource for all MISP galaxy clusters.

A [readable PDF overview of the MISP galaxy is available](https://www.misp.software/galaxy.pdf) or [HTML](https://www.misp.software/galaxy.html) and generated from the JSON.

## How to contribute?

- [Read the contribution document](CONTRIBUTE.md)

## License

The MISP galaxy (JSON files) are dual-licensed under:

- [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/legalcode) (CC0 1.0) - Public Domain Dedication.

or

~~~~
 Copyright (c) 2015-2024 Alexandre Dulaunoy - a@foo.be
 Copyright (c) 2015-2024 CIRCL - Computer Incident Response Center Luxembourg
 Copyright (c) 2015-2024 Andras Iklody
 Copyright (c) 2015-2024 Raphael Vinot
 Copyright (c) 2015-2024 Deborah Servili
 Copyright (c) 2016-2024 Various contributors to MISP Project

 Redistribution and use in source and binary forms, with or without modification,
 are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 OF THE POSSIBILITY OF SUCH DAMAGE.
~~~~~
