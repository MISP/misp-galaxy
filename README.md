# misp-galaxy

MISP galaxy is a simple method to express a large object called cluster that can be attached to MISP events or
attributes. A cluster can be composed of one or more elements. Elements are expressed as key-values. There
are default elements available in MISP galaxy but those can overwritten, replaced or updated as you wish.

Existing clusters and elements can be used as-is or as a template. MISP distribution can be applied
to each cluster to permit limited or a broader distribution scheme.

# Available clusters

- [cluster/threat-actor.json](cluster/threat-actor.json) - Threat Actor

# Available Elements

- [elements/apt-groups.json](elements/apt-groups.json) - APT Groups - Known or estimated adversary groups targeting organizations and employees. Adversary groups are regularly confused with their initial operation or campaign.
- [elements/threat-actor-motivation-vocabulary.json](elements/threat-actor-motivation-vocabulary.json) - The MotivationVocab is the default STIX vocabulary for expressing the motivation of a threat actor. STIX 1.2.1
- [elements/threat-actor-intended-effect-vocabulary.json](elements/threat-actor-intended-effect-vocabulary.json) - The IntendedEffectVocab is the default STIX vocabulary for expressing the intended effect of a threat actor. STIX 1.2.1

## How to contribute?

Fork the project, update or create elements or clusters and make a pull-request.

