# misp-galaxy

![Python application](https://github.com/MISP/misp-galaxy/workflows/Python%20application/badge.svg)

MISP galaxy is a simple method to express a large object called cluster that can be attached to MISP events or
attributes. A cluster can be composed of one or more elements. Elements are expressed as key-values. There
are default vocabularies available in MISP galaxy but those can be overwritten, replaced or updated as you wish.

Existing clusters and vocabularies can be used as-is or as a template. MISP distribution can be applied
to each cluster to permit a limited or broader distribution scheme.

Vocabularies are from existing standards (like STIX, Veris, MISP and so on) or custom ones.

The objective is to have a comment set of clusters for organizations starting analysis but that can be expanded
to localized information (which is not shared) or additional information (that can be shared).

# Available clusters

- [clusters/android.json](clusters/android.json) - Android malware galaxy based on multiple open sources.
- [clusters/banker.json](clusters/banker.json) - A list of banker malware.
- [clusters/stealer.json](clusters/stealer.json) - A list of malware stealer.
- [clusters/backdoor.json](clusters/backdoor.json) - A list of backdoor malware.
- [clusters/botnet.json](clusters/botnet.json) - A list of known botnets.
- [clusters/branded_vulnerability.json](clusters/branded_vulnerability.json) - List of known vulnerabilities and exploits.
- [clusters/exploit-kit.json](clusters/exploit-kit.json) - Exploit-Kit is an enumeration of some exploitation kits used by adversaries. The list includes document, browser and router exploit kits. It's not meant to be totally exhaustive but aim at covering the most seen in the past 5 years.
- [clusters/microsoft-activity-group.json](clusters/microsoft-activity-group.json) - Activity groups as described by Microsoft.
- [clusters/preventive-measure.json](clusters/preventive-measure.json) - Preventive measures.
- [clusters/ransomware.json](clusters/ransomware.json) - Ransomware galaxy based on https://docs.google.com/spreadsheets/d/1TWS238xacAto-fLKh1n5uTsdijWdCEsGIM0Y0Hvmc5g/pubhtml
- [clusters/rat.json](clusters/rat.json) - remote administration tool or remote access tool (RAT), also called sometimes remote access trojan, is a piece of software or programming that allows a remote "operator" to control a system as if they have physical access to that system.
- [clusters/tds.json](clusters/tds.json) - TDS is a list of Traffic Direction System used by adversaries.
- [clusters/threat-actor.json](clusters/threat-actor.json) - Adversary groups - Known or estimated adversary groups targeting organizations and employees. Adversary groups are regularly confused with their initial operation or campaign. MISP
- [clusters/tool.json](clusters/tool.json) - tool is an enumeration of tools used by adversaries. The list includes malware but also common software regularly used by the adversaries.

- [clusters/mitre-attack-pattern.json](clusters/mitre-attack-pattern.json) - Attack Pattern - MITRE Adversarial Tactics, Techniques & Common Knowledge (ATT&CK) - v2.0
- [clusters/mitre-course-of-action.json](clusters/mitre-course-of-action.json) - Course of Action - MITRE Adversarial Tactics, Techniques & Common Knowledge (ATT&CK) - v2.0
- [clusters/mitre-intrusion-set.json](clusters/mitre-intrusion-set.json) - Intrusion Set - MITRE Adversarial Tactics, Techniques & Common Knowledge (ATT&CK) - v2.0
- [clusters/mitre-malware.json](clusters/mitre-malware.json) - Malware - MITRE Adversarial Tactics, Techniques & Common Knowledge (ATT&CK) - v2.0
- [clusters/mitre-tool.json](clusters/mitre-tool.json) - Tool - MITRE Adversarial Tactics, Techniques & Common Knowledge (ATT&CK) - v2.0

- [clusters/mitre-ics-assets.json](clusters/mitre-ics-assets.json) - ICS Assets - A list of asset categories that are commonly found in industrial control systems.
- [clusters/mitre-ics-groups.json](clusters/mitre-ics-groups.json) - ICS Groups - Groups are sets of related intrusion activity that are tracked by a common name in the security community.
- [clusters/mitre-ics-levels.json](clusters/mitre-ics-levels.json) - ICS Levels - Based on the Purdue Model to aid ATT&CK for ICS users to understand which techniques are applicable to their environment.
- [clusters/mitre-ics-software.json](clusters/mitre-ics-software.json) - ICS Software - Software is a generic term for custom or commercial code, operating system utilities, open-source software, or other tools used to conduct behavior modeled in ATT&CK for ICS.
- [clusters/mitre-ics-tactics.json](clusters/mitre-ics-tactics.json) - ICS Tectics - A list of all tactics in ATT&CK for ICS.
- [clusters/mitre-ics-techniques.json](clusters/mitre-ics-techniques.json) - ICS Techniques - A list of Techniques in ATT&CK for ICS.

- [clusters/sectors.json](clusters/sectors.json) - Activity sectors
- [clusters/cert-eu-govsector.json](clusters/cert-eu-govsector.json) - Cert EU GovSector
- [clusters/social-dark-patterns.json](clusters/social-dark-patterns.json) - Social Engineering - Dark Patterns

# Available Vocabularies

A [readable PDF overview of the MISP galaxy is available](https://www.misp.software/galaxy.pdf) or [HTML](https://www.misp.software/galaxy.html) and generated from the JSON.


## Common

- [vocabularies/common/certainty-level.json](vocabularies/common/certainty-level.json) - Certainty level of an associated element or cluster.
- [vocabularies/common/threat-actor-type.json](vocabularies/common/threat-actor-type.json) - threat actor type vocab as defined by Cert EU.
- [vocabularies/common/ttp-category.json](vocabularies/common/ttp-category.json) - ttp category vocab as defined by Cert EU.
- [vocabularies/common/ttp-type.json](vocabularies/common/ttp-type.json) - ttp type vocab as defined by Cert EU.

## Threat Actor

- [vocabularies/threat-actor/cert-eu-motive.json](vocabularies/threat-actor/cert-eu-motive.json) - Motive vocab as defined by Cert EU.
- [vocabularies/threat-actor/intended-effect-vocabulary.json](vocabularies/threat-actor/intended-effect.json) - The IntendedEffectVocab is the default STIX vocabulary for expressing the intended effect of a threat actor. STIX 1.2.1
- [vocabularies/threat-actor/motivation-vocabulary.json](vocabularies/threat-actor/motivation.json) - The MotivationVocab is the default STIX vocabulary for expressing the motivation of a threat actor. STIX 1.2.1
- [vocabularies/threat-actor/planning-and-operational-support-vocabulary.json](vocabularies/threat-actor/planning-and-operational-support.json) - The PlanningAndOperationalSupportVocab is the default STIX vocabulary for expressing the planning and operational support functions available to a threat actor.
- [vocabularies/threat-actor/sophistication.json](vocabularies/threat-actor/sophistication.json) - The ThreatActorSophisticationVocab enumeration is used to define the default STIX vocabulary for expressing the subjective level of sophistication of a threat actor.
- [vocabularies/threat-actor/type.json](vocabularies/threat-actor/type.json) - The ThreatActorTypeVocab enumeration is used to define the default STIX vocabulary for expressing the subjective type of a threat actor.

## MISP Integration

Starting from [MISP 2.4.56](http://www.misp-project.org/2016/12/07/MISP.2.4.56.released.html), galaxy is integrated within the MISP threat sharing platform and users can directly benefit from the available clusters to attach them to the MISP event.

![MISP Integration of the MISP galaxy](doc/images/screenshot.png)
## How to contribute?

- [Read the contribution document](CONTRIBUTE.md)

## License

The MISP galaxy (JSON files) are dual-licensed under:

- [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/legalcode) (CC0 1.0) - Public Domain Dedication.

or

~~~~
 Copyright (c) 2015-2019 Alexandre Dulaunoy - a@foo.be
 Copyright (c) 2015-2019 CIRCL - Computer Incident Response Center Luxembourg
 Copyright (c) 2015-2019 Andras Iklody
 Copyright (c) 2015-2019 Raphael Vinot
 Copyright (c) 2015-2019 Deborah Servili
 Copyright (c) 2016-2019 Various contributors to MISP Project

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
