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

[360.net Threat Actors](https://www.misp-project.org/galaxy.html#_360.net_threat_actors) - Known or estimated adversary groups as identified by 360.net.

Category: *actor* - source: *https://apt.360.net/aptlist* - total: *42* elements

[[HTML](https://www.misp-project.org/galaxy.html#_360.net_threat_actors)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/360net.json)]

## Android

[Android](https://www.misp-project.org/galaxy.html#_android) - Android malware galaxy based on multiple open sources.

Category: *tool* - source: *Open Sources* - total: *433* elements

[[HTML](https://www.misp-project.org/galaxy.html#_android)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/android.json)]

## Azure Threat Research Matrix

[Azure Threat Research Matrix](https://www.misp-project.org/galaxy.html#_azure_threat_research_matrix) - The purpose of the Azure Threat Research Matrix (ATRM) is to educate readers on the potential of Azure-based tactics, techniques, and procedures (TTPs). It is not to teach how to weaponize or specifically abuse them. For this reason, some specific commands will be obfuscated or parts will be omitted to prevent abuse.

Category: *atrm* - source: *https://github.com/microsoft/Azure-Threat-Research-Matrix* - total: *89* elements

[[HTML](https://www.misp-project.org/galaxy.html#_azure_threat_research_matrix)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/atrm.json)]

## attck4fraud

[attck4fraud](https://www.misp-project.org/galaxy.html#_attck4fraud) - attck4fraud - Principles of MITRE ATT&CK in the fraud domain

Category: *guidelines* - source: *Open Sources* - total: *31* elements

[[HTML](https://www.misp-project.org/galaxy.html#_attck4fraud)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/attck4fraud.json)]

## Backdoor

[Backdoor](https://www.misp-project.org/galaxy.html#_backdoor) - A list of backdoor malware.

Category: *tool* - source: *Open Sources* - total: *13* elements

[[HTML](https://www.misp-project.org/galaxy.html#_backdoor)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/backdoor.json)]

## Banker

[Banker](https://www.misp-project.org/galaxy.html#_banker) - A list of banker malware.

Category: *tool* - source: *Open Sources* - total: *53* elements

[[HTML](https://www.misp-project.org/galaxy.html#_banker)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/banker.json)]

## Bhadra Framework

[Bhadra Framework](https://www.misp-project.org/galaxy.html#_bhadra_framework) - Bhadra Threat Modeling Framework

Category: *mobile* - source: *https://arxiv.org/pdf/2005.05110.pdf* - total: *47* elements

[[HTML](https://www.misp-project.org/galaxy.html#_bhadra_framework)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/bhadra-framework.json)]

## Botnet

[Botnet](https://www.misp-project.org/galaxy.html#_botnet) - botnet galaxy

Category: *tool* - source: *MISP Project* - total: *75* elements

[[HTML](https://www.misp-project.org/galaxy.html#_botnet)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/botnet.json)]

## Branded Vulnerability

[Branded Vulnerability](https://www.misp-project.org/galaxy.html#_branded_vulnerability) - List of known vulnerabilities and attacks with a branding

Category: *vulnerability* - source: *Open Sources* - total: *14* elements

[[HTML](https://www.misp-project.org/galaxy.html#_branded_vulnerability)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/branded_vulnerability.json)]

## Cert EU GovSector

[Cert EU GovSector](https://www.misp-project.org/galaxy.html#_cert_eu_govsector) - Cert EU GovSector

Category: *sector* - source: *CERT-EU* - total: *6* elements

[[HTML](https://www.misp-project.org/galaxy.html#_cert_eu_govsector)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/cert-eu-govsector.json)]

## China Defence Universities Tracker

[China Defence Universities Tracker](https://www.misp-project.org/galaxy.html#_china_defence_universities_tracker) - The China Defence Universities Tracker is a database of Chinese institutions engaged in military or security-related science and technology research. It was created by ASPI’s International Cyber Policy Centre.

Category: *academic-institution* - source: *ASPI International Cyber Policy Centre* - total: *159* elements

[[HTML](https://www.misp-project.org/galaxy.html#_china_defence_universities_tracker)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/china-defence-universities.json)]

## CONCORDIA Mobile Modelling Framework - Attack Pattern

[CONCORDIA Mobile Modelling Framework - Attack Pattern](https://www.misp-project.org/galaxy.html#_concordia_mobile_modelling_framework_-_attack_pattern) - A list of Techniques in CONCORDIA Mobile Modelling Framework.

Category: *cmtmf-attack-pattern* - source: *https://5g4iot.vlab.cs.hioa.no/* - total: *93* elements

[[HTML](https://www.misp-project.org/galaxy.html#_concordia_mobile_modelling_framework_-_attack_pattern)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/cmtmf-attack-pattern.json)]

## Country

[Country](https://www.misp-project.org/galaxy.html#_country) - Country meta information based on the database provided by geonames.org.

Category: *country* - source: *MISP Project* - total: *252* elements

[[HTML](https://www.misp-project.org/galaxy.html#_country)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/country.json)]

## Cryptominers

[Cryptominers](https://www.misp-project.org/galaxy.html#_cryptominers) - A list of cryptominer and cryptojacker malware.

Category: *Cryptominers* - source: *Open Source Intelligence* - total: *5* elements

[[HTML](https://www.misp-project.org/galaxy.html#_cryptominers)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/cryptominers.json)]

## Election guidelines

[Election guidelines](https://www.misp-project.org/galaxy.html#_election_guidelines) - Universal Development and Security Guidelines as Applicable to Election Technology.

Category: *guidelines* - source: *Open Sources* - total: *23* elements

[[HTML](https://www.misp-project.org/galaxy.html#_election_guidelines)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/election-guidelines.json)]

## Exploit-Kit

[Exploit-Kit](https://www.misp-project.org/galaxy.html#_exploit-kit) - Exploit-Kit is an enumeration of some exploitation kits used by adversaries. The list includes document, browser and router exploit kits.It's not meant to be totally exhaustive but aim at covering the most seen in the past 5 years

Category: *tool* - source: *MISP Project* - total: *52* elements

[[HTML](https://www.misp-project.org/galaxy.html#_exploit-kit)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/exploit-kit.json)]

## FIRST DNS Abuse Techniques Matrix

[FIRST DNS Abuse Techniques Matrix](https://www.misp-project.org/galaxy.html#_first_dns_abuse_techniques_matrix) - The Domain Name System (DNS) is a critical part of the Internet, including mapping domain names to IP addresses. Malicious threat actors use domain names, their corresponding technical resources, and other parts of the DNS infrastructure, including its protocols, for their malicious cyber operations. CERTs are confronted with reported DNS abuse on a continuous basis, and rely heavily on DNS analysis and infrastructure to protect their constituencies. Understanding the international customary norms applicable for detecting and mitigating DNS abuse from the perspective of the global incident response community is critical for the open Internet’s stability, security and resiliency. See also https://www.first.org/global/sigs/dns/ for more information.

Category: *first-dns* - source: *https://www.first.org/global/sigs/dns/* - total: *21* elements

[[HTML](https://www.misp-project.org/galaxy.html#_first_dns_abuse_techniques_matrix)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/first-dns.json)]

## Malpedia

[Malpedia](https://www.misp-project.org/galaxy.html#_malpedia) - Malware galaxy cluster based on Malpedia.

Category: *tool* - source: *Malpedia* - total: *2574* elements

[[HTML](https://www.misp-project.org/galaxy.html#_malpedia)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/malpedia.json)]

## Microsoft Activity Group actor

[Microsoft Activity Group actor](https://www.misp-project.org/galaxy.html#_microsoft_activity_group_actor) - Activity groups as described by Microsoft

Category: *actor* - source: *MISP Project* - total: *14* elements

[[HTML](https://www.misp-project.org/galaxy.html#_microsoft_activity_group_actor)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/microsoft-activity-group.json)]

## Misinformation Pattern

[Misinformation Pattern](https://www.misp-project.org/galaxy.html#_misinformation_pattern) - AM!TT Technique

Category: *misinformation-pattern* - source: *https://github.com/misinfosecproject/amitt_framework* - total: *61* elements

[[HTML](https://www.misp-project.org/galaxy.html#_misinformation_pattern)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/misinfosec-amitt-misinformation-pattern.json)]

## Attack Pattern

[Attack Pattern](https://www.misp-project.org/galaxy.html#_attack_pattern) - ATT&CK tactic

Category: *attack-pattern* - source: *https://github.com/mitre/cti* - total: *1086* elements

[[HTML](https://www.misp-project.org/galaxy.html#_attack_pattern)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-attack-pattern.json)]

## Course of Action

[Course of Action](https://www.misp-project.org/galaxy.html#_course_of_action) - ATT&CK Mitigation

Category: *course-of-action* - source: *https://github.com/mitre/cti* - total: *279* elements

[[HTML](https://www.misp-project.org/galaxy.html#_course_of_action)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-course-of-action.json)]

## Enterprise Attack - Attack Pattern

[Enterprise Attack - Attack Pattern](https://www.misp-project.org/galaxy.html#_enterprise_attack_-_attack_pattern) - ATT&CK tactic

Category: *attack-pattern* - source: *https://github.com/mitre/cti* - total: *219* elements

[[HTML](https://www.misp-project.org/galaxy.html#_enterprise_attack_-_attack_pattern)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-enterprise-attack-attack-pattern.json)]

## Enterprise Attack - Course of Action

[Enterprise Attack - Course of Action](https://www.misp-project.org/galaxy.html#_enterprise_attack_-_course_of_action) - ATT&CK Mitigation

Category: *course-of-action* - source: *https://github.com/mitre/cti* - total: *215* elements

[[HTML](https://www.misp-project.org/galaxy.html#_enterprise_attack_-_course_of_action)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-enterprise-attack-course-of-action.json)]

## Enterprise Attack - Intrusion Set

[Enterprise Attack - Intrusion Set](https://www.misp-project.org/galaxy.html#_enterprise_attack_-_intrusion_set) - Name of ATT&CK Group

Category: *actor* - source: *https://github.com/mitre/cti* - total: *69* elements

[[HTML](https://www.misp-project.org/galaxy.html#_enterprise_attack_-_intrusion_set)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-enterprise-attack-intrusion-set.json)]

## Enterprise Attack - Malware

[Enterprise Attack - Malware](https://www.misp-project.org/galaxy.html#_enterprise_attack_-_malware) - Name of ATT&CK software

Category: *tool* - source: *https://github.com/mitre/cti* - total: *188* elements

[[HTML](https://www.misp-project.org/galaxy.html#_enterprise_attack_-_malware)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-enterprise-attack-malware.json)]

## Enterprise Attack - Tool

[Enterprise Attack - Tool](https://www.misp-project.org/galaxy.html#_enterprise_attack_-_tool) - Name of ATT&CK software

Category: *tool* - source: *https://github.com/mitre/cti* - total: *45* elements

[[HTML](https://www.misp-project.org/galaxy.html#_enterprise_attack_-_tool)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-enterprise-attack-tool.json)]

## Assets

[Assets](https://www.misp-project.org/galaxy.html#_assets) - A list of asset categories that are commonly found in industrial control systems.

Category: *asset* - source: *https://collaborate.mitre.org/attackics/index.php/All_Assets* - total: *7* elements

[[HTML](https://www.misp-project.org/galaxy.html#_assets)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-ics-assets.json)]

## Groups

[Groups](https://www.misp-project.org/galaxy.html#_groups) - Groups are sets of related intrusion activity that are tracked by a common name in the security community. Groups are also sometimes referred to as campaigns or intrusion sets. Some groups have multiple names associated with the same set of activities due to various organizations tracking the same set of activities by different names. Groups are mapped to publicly reported technique use and referenced in the ATT&CK for ICS knowledge base. Groups are also mapped to reported software used during intrusions.

Category: *actor* - source: *https://collaborate.mitre.org/attackics/index.php/Groups* - total: *10* elements

[[HTML](https://www.misp-project.org/galaxy.html#_groups)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-ics-groups.json)]

## Levels

[Levels](https://www.misp-project.org/galaxy.html#_levels) - Based on the Purdue Model to aid ATT&CK for ICS users to understand which techniques are applicable to their environment.

Category: *level* - source: *https://collaborate.mitre.org/attackics/index.php/All_Levels* - total: *3* elements

[[HTML](https://www.misp-project.org/galaxy.html#_levels)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-ics-levels.json)]

## Software

[Software](https://www.misp-project.org/galaxy.html#_software) - Software is a generic term for custom or commercial code, operating system utilities, open-source software, or other tools used to conduct behavior modeled in ATT&CK for ICS.

Category: *tool* - source: *https://collaborate.mitre.org/attackics/index.php/Software* - total: *17* elements

[[HTML](https://www.misp-project.org/galaxy.html#_software)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-ics-software.json)]

## Tactics

[Tactics](https://www.misp-project.org/galaxy.html#_tactics) - A list of all 11 tactics in ATT&CK for ICS

Category: *tactic* - source: *https://collaborate.mitre.org/attackics/index.php/All_Tactics* - total: *9* elements

[[HTML](https://www.misp-project.org/galaxy.html#_tactics)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-ics-tactics.json)]

## Techniques

[Techniques](https://www.misp-project.org/galaxy.html#_techniques) - A list of Techniques in ATT&CK for ICS.

Category: *attack-pattern* - source: *https://collaborate.mitre.org/attackics/index.php/All_Techniques* - total: *78* elements

[[HTML](https://www.misp-project.org/galaxy.html#_techniques)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-ics-techniques.json)]

## Intrusion Set

[Intrusion Set](https://www.misp-project.org/galaxy.html#_intrusion_set) - Name of ATT&CK Group

Category: *actor* - source: *https://github.com/mitre/cti* - total: *148* elements

[[HTML](https://www.misp-project.org/galaxy.html#_intrusion_set)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-intrusion-set.json)]

## Malware

[Malware](https://www.misp-project.org/galaxy.html#_malware) - Name of ATT&CK software

Category: *tool* - source: *https://github.com/mitre/cti* - total: *633* elements

[[HTML](https://www.misp-project.org/galaxy.html#_malware)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-malware.json)]

## Mobile Attack - Attack Pattern

[Mobile Attack - Attack Pattern](https://www.misp-project.org/galaxy.html#_mobile_attack_-_attack_pattern) - ATT&CK tactic

Category: *attack-pattern* - source: *https://github.com/mitre/cti* - total: *76* elements

[[HTML](https://www.misp-project.org/galaxy.html#_mobile_attack_-_attack_pattern)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-mobile-attack-attack-pattern.json)]

## Mobile Attack - Course of Action

[Mobile Attack - Course of Action](https://www.misp-project.org/galaxy.html#_mobile_attack_-_course_of_action) - ATT&CK Mitigation

Category: *course-of-action* - source: *https://github.com/mitre/cti* - total: *14* elements

[[HTML](https://www.misp-project.org/galaxy.html#_mobile_attack_-_course_of_action)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-mobile-attack-course-of-action.json)]

## Mobile Attack - Intrusion Set

[Mobile Attack - Intrusion Set](https://www.misp-project.org/galaxy.html#_mobile_attack_-_intrusion_set) - Name of ATT&CK Group

Category: *actor* - source: *https://github.com/mitre/cti* - total: *1* elements

[[HTML](https://www.misp-project.org/galaxy.html#_mobile_attack_-_intrusion_set)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-mobile-attack-intrusion-set.json)]

## Mobile Attack - Malware

[Mobile Attack - Malware](https://www.misp-project.org/galaxy.html#_mobile_attack_-_malware) - Name of ATT&CK software

Category: *tool* - source: *https://github.com/mitre/cti* - total: *35* elements

[[HTML](https://www.misp-project.org/galaxy.html#_mobile_attack_-_malware)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-mobile-attack-malware.json)]

## Mobile Attack - Tool

[Mobile Attack - Tool](https://www.misp-project.org/galaxy.html#_mobile_attack_-_tool) - Name of ATT&CK software

Category: *tool* - source: *https://github.com/mitre/cti* - total: *1* elements

[[HTML](https://www.misp-project.org/galaxy.html#_mobile_attack_-_tool)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-mobile-attack-tool.json)]

## Pre Attack - Attack Pattern

[Pre Attack - Attack Pattern](https://www.misp-project.org/galaxy.html#_pre_attack_-_attack_pattern) - ATT&CK tactic

Category: *attack-pattern* - source: *https://github.com/mitre/cti* - total: *174* elements

[[HTML](https://www.misp-project.org/galaxy.html#_pre_attack_-_attack_pattern)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-pre-attack-attack-pattern.json)]

## Pre Attack - Intrusion Set

[Pre Attack - Intrusion Set](https://www.misp-project.org/galaxy.html#_pre_attack_-_intrusion_set) - Name of ATT&CK Group

Category: *actor* - source: *https://github.com/mitre/cti* - total: *7* elements

[[HTML](https://www.misp-project.org/galaxy.html#_pre_attack_-_intrusion_set)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-pre-attack-intrusion-set.json)]

## Tool

[Tool](https://www.misp-project.org/galaxy.html#_tool) - Name of ATT&CK software

Category: *tool* - source: *https://github.com/mitre/cti* - total: *82* elements

[[HTML](https://www.misp-project.org/galaxy.html#_tool)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-tool.json)]

## o365-exchange-techniques

[o365-exchange-techniques](https://www.misp-project.org/galaxy.html#_o365-exchange-techniques) - o365-exchange-techniques - Office365/Exchange related techniques by @johnLaTwC and @inversecos

Category: *guidelines* - source: *Open Sources, https://www.inversecos.com/2021/09/office365-attacks-bypassing-mfa.html* - total: *62* elements

[[HTML](https://www.misp-project.org/galaxy.html#_o365-exchange-techniques)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/o365-exchange-techniques.json)]

## Preventive Measure

[Preventive Measure](https://www.misp-project.org/galaxy.html#_preventive_measure) - Preventive measures based on the ransomware document overview as published in https://docs.google.com/spreadsheets/d/1TWS238xacAto-fLKh1n5uTsdijWdCEsGIM0Y0Hvmc5g/pubhtml# . The preventive measures are quite generic and can fit any standard Windows infrastructure and their security measures.

Category: *measure* - source: *MISP Project* - total: *20* elements

[[HTML](https://www.misp-project.org/galaxy.html#_preventive_measure)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/preventive-measure.json)]

## Ransomware

[Ransomware](https://www.misp-project.org/galaxy.html#_ransomware) - Ransomware galaxy based on https://docs.google.com/spreadsheets/d/1TWS238xacAto-fLKh1n5uTsdijWdCEsGIM0Y0Hvmc5g/pubhtml and http://pastebin.com/raw/GHgpWjar

Category: *tool* - source: *Various* - total: *1649* elements

[[HTML](https://www.misp-project.org/galaxy.html#_ransomware)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/ransomware.json)]

## RAT

[RAT](https://www.misp-project.org/galaxy.html#_rat) - remote administration tool or remote access tool (RAT), also called sometimes remote access trojan, is a piece of software or programming that allows a remote "operator" to control a system as if they have physical access to that system.

Category: *tool* - source: *MISP Project* - total: *265* elements

[[HTML](https://www.misp-project.org/galaxy.html#_rat)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/rat.json)]

## Regions UN M49

[Regions UN M49](https://www.misp-project.org/galaxy.html#_regions_un_m49) - Regions based on UN M49.

Category: *location* - source: *https://unstats.un.org/unsd/methodology/m49/overview/* - total: *32* elements

[[HTML](https://www.misp-project.org/galaxy.html#_regions_un_m49)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/region.json)]

## rsit

[rsit](https://www.misp-project.org/galaxy.html#_rsit) - rsit

Category: *rsit* - source: *https://github.com/enisaeu/Reference-Security-Incident-Taxonomy-Task-Force* - total: *39* elements

[[HTML](https://www.misp-project.org/galaxy.html#_rsit)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/rsit.json)]

## Sector

[Sector](https://www.misp-project.org/galaxy.html#_sector) - Activity sectors

Category: *sector* - source: *CERT-EU* - total: *117* elements

[[HTML](https://www.misp-project.org/galaxy.html#_sector)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/sector.json)]

## Sigma-Rules

[Sigma-Rules](https://www.misp-project.org/galaxy.html#_sigma-rules) - MISP galaxy cluster based on Sigma Rules.

Category: *rules* - source: *https://github.com/jstnk9/MISP/tree/main/misp-galaxy/sigma* - total: *2696* elements

[[HTML](https://www.misp-project.org/galaxy.html#_sigma-rules)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/sigma-rules.json)]

## Dark Patterns

[Dark Patterns](https://www.misp-project.org/galaxy.html#_dark_patterns) - Dark Patterns are user interface that tricks users into making decisions that benefit the interface's holder to the expense of the user.

Category: *dark-patterns* - source: *CIRCL* - total: *19* elements

[[HTML](https://www.misp-project.org/galaxy.html#_dark_patterns)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/social-dark-patterns.json)]

## SoD Matrix

[SoD Matrix](https://www.misp-project.org/galaxy.html#_sod_matrix) - SOD Matrix

Category: *sod-matrix* - source: *https://github.com/cudeso/SoD-Matrix* - total: *276* elements

[[HTML](https://www.misp-project.org/galaxy.html#_sod_matrix)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/sod-matrix.json)]

## Stealer

[Stealer](https://www.misp-project.org/galaxy.html#_stealer) - A list of malware stealer.

Category: *tool* - source: *Open Sources* - total: *12* elements

[[HTML](https://www.misp-project.org/galaxy.html#_stealer)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/stealer.json)]

## Surveillance Vendor

[Surveillance Vendor](https://www.misp-project.org/galaxy.html#_surveillance_vendor) - List of vendors selling surveillance technologies including malware, interception devices or computer exploitation services.

Category: *actor* - source: *MISP Project* - total: *15* elements

[[HTML](https://www.misp-project.org/galaxy.html#_surveillance_vendor)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/surveillance-vendor.json)]

## Target Information

[Target Information](https://www.misp-project.org/galaxy.html#_target_information) - Description of targets of threat actors.

Category: *target* - source: *Various* - total: *240* elements

[[HTML](https://www.misp-project.org/galaxy.html#_target_information)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/target-information.json)]

## TDS

[TDS](https://www.misp-project.org/galaxy.html#_tds) - TDS is a list of Traffic Direction System used by adversaries

Category: *tool* - source: *MISP Project* - total: *11* elements

[[HTML](https://www.misp-project.org/galaxy.html#_tds)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/tds.json)]

## Tea Matrix

[Tea Matrix](https://www.misp-project.org/galaxy.html#_tea_matrix) - Tea Matrix

Category: *tea-matrix* - source: ** - total: *7* elements

[[HTML](https://www.misp-project.org/galaxy.html#_tea_matrix)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/tea-matrix.json)]

## Threat Actor

[Threat Actor](https://www.misp-project.org/galaxy.html#_threat_actor) - Known or estimated adversary groups targeting organizations and employees. Adversary groups are regularly confused with their initial operation or campaign. threat-actor-classification meta can be used to clarify the understanding of the threat-actor if also considered as operation, campaign or activity group.

Category: *actor* - source: *MISP Project* - total: *418* elements

[[HTML](https://www.misp-project.org/galaxy.html#_threat_actor)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/threat-actor.json)]

## Tool

[Tool](https://www.misp-project.org/galaxy.html#_tool) - threat-actor-tools is an enumeration of tools used by adversaries. The list includes malware but also common software regularly used by the adversaries.

Category: *tool* - source: *MISP Project* - total: *549* elements

[[HTML](https://www.misp-project.org/galaxy.html#_tool)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/tool.json)]

## UAVs/UCAVs

[UAVs/UCAVs](https://www.misp-project.org/galaxy.html#_uavs/ucavs) - Unmanned Aerial Vehicles / Unmanned Combat Aerial Vehicles

Category: *military equipment* - source: *Popular Mechanics* - total: *36* elements

[[HTML](https://www.misp-project.org/galaxy.html#_uavs/ucavs)] - [[JSON](https://github.com/MISP/misp-galaxy/blob/main/clusters/uavs.json)]

# Online documentation 

A [readable PDF overview of the MISP galaxy is available](https://www.misp.software/galaxy.pdf) or [HTML](https://www.misp.software/galaxy.html) and generated from the JSON.

## How to contribute?

- [Read the contribution document](CONTRIBUTE.md)

## License

The MISP galaxy (JSON files) are dual-licensed under:

- [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/legalcode) (CC0 1.0) - Public Domain Dedication.

or

~~~~
 Copyright (c) 2015-2022 Alexandre Dulaunoy - a@foo.be
 Copyright (c) 2015-2022 CIRCL - Computer Incident Response Center Luxembourg
 Copyright (c) 2015-2022 Andras Iklody
 Copyright (c) 2015-2022 Raphael Vinot
 Copyright (c) 2015-2022 Deborah Servili
 Copyright (c) 2016-2022 Various contributors to MISP Project

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
