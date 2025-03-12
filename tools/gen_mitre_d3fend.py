#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    A simple convertor of the MITRE D3FEND to a MISP Galaxy datastructure.
#    Copyright (C) 2024 Christophe Vandeplas
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests
import uuid
from pymispgalaxies import Cluster, Galaxy


d3fend_url = 'https://d3fend.mitre.org/ontologies/d3fend.json'
d3fend_full_mappings_url = 'https://d3fend.mitre.org/api/ontology/inference/d3fend-full-mappings.json'


galaxy_fname = 'mitre-d3fend.json'
galaxy_type = "mitre-d3fend"
galaxy_name = "MITRE D3FEND"
galaxy_description = 'A knowledge graph of cybersecurity countermeasures.'
galaxy_source = 'https://d3fend.mitre.org/'


# we love eating lots of memory
r = requests.get(d3fend_url)
d3fend_json = r.json()

r = requests.get(d3fend_full_mappings_url)
d3fend_mappings_json = r.json()


uuid_seed = '35527064-12b4-4b73-952b-6d76b9f1b1e3'

tactics = {}   # key = tactic, value = phases
phases_ids = []
techniques_ids = []
techniques = []
relations = {}


def get_as_list(item):
    if isinstance(item, dict):
        return item.values()
    elif isinstance(item, list):
        result = []
        for i in item:
            if isinstance(i, dict):
                result += i.values()
            if isinstance(i, str):
                result.append(i)
        return result
    elif isinstance(item, str):
        return [item]
    else:
        raise ValueError(f'Unexpected type: {type(item)}')


def is_val_in_element(val, element):
    result = False
    if isinstance(element, dict):  # only one entry
        if val == element['@id']:
            return True
    elif isinstance(element, list):  # multiple entries
        for e in element:
            if val == e['@id']:
                return True
    elif not element:
        pass
    else:
        raise ValueError(f'Unexpected type: {type(element)}')
    return result


def is_element_in_list(element, lst):
    if isinstance(element, dict):  # only one entry
        if element['@id'] in lst:
            return True

    elif isinstance(element, list):  # multiple entries
        for e in element:
            if e['@id'] in lst:
                return True
    else:
        raise ValueError(f'Unexpected type: {type(element)}')


def id_to_label(id):
    return data[id]['rdfs:label']


def get_parent(item):
    # value of subClassOf starts with d3f
    if 'rdfs:subClassOf' in item:
        # if 'd3f:enables' in item:
        #     parent_classes = get_as_list(item['d3f:enables'])
        # else:
        parent_classes = get_as_list(item['rdfs:subClassOf'])
        for parent_class in parent_classes:
            if parent_class.startswith('d3f'):
                return parent_class
    return None


def find_kill_chain_of(original_item):
    # find if back in the kill chain_tactics list we built before
    parent_classes = get_as_list(original_item['rdfs:subClassOf'])
    for parent_class in parent_classes:
        if parent_class.startswith('d3f'):
            parent_class_name = id_to_label(parent_class).replace(' ', '-')
            for tactic, phases in kill_chain_tactics.items():
                if parent_class_name in phases:
                    return f"{tactic}:{parent_class_name}"
    # child with one more parent in between
    for parent_class in parent_classes:
        if parent_class.startswith('d3f'):
            return find_kill_chain_of(data[parent_class])


mitre_attack_pattern = Cluster('mitre-attack-pattern')


def find_mitre_uuid_from_technique_id(technique_id):
    try:
        return mitre_attack_pattern.get_by_external_id(technique_id).uuid
    except KeyError:
        print("No MITRE UUID found for technique_id: ", technique_id)
        return None


try:
    cluster = Cluster('mitre-d3fend')
except (KeyError, FileNotFoundError):
    cluster = Cluster({
        'authors': ["MITRE"],
        'category': 'd3fend',
        'name': galaxy_name,
        'description': galaxy_description,
        'source': galaxy_source,
        'type': galaxy_type,
        'uuid': "b8bd7e45-63bf-4c44-8ab1-c81c82547380",
        'version': 0
    })

# relationships
for item in d3fend_mappings_json['results']['bindings']:
    d3fend_technique = item['def_tech_label']['value']
    attack_technique = item['off_tech_label']['value']
    attack_technique_id = item['off_tech']['value'].split('#')[-1]
    # print(f"Mapping: {d3fend_technique} -> {attack_technique} ({attack_technique_id})")
    dest_uuid = find_mitre_uuid_from_technique_id(attack_technique_id)
    if dest_uuid:
        rel_type = item['def_artifact_rel_label']['value']
        if d3fend_technique not in relations:
            relations[d3fend_technique] = []
        relations[d3fend_technique].append(
            {
                'dest-uuid': dest_uuid,
                'type': rel_type
            }
        )


# first convert as dict with key = @id
data = {}
for item in d3fend_json['@graph']:
    data[item['@id']] = item

# tactic
for item in d3fend_json['@graph']:
    if is_val_in_element('d3f:DefensiveTactic', item.get('rdfs:subClassOf')):
        tactics[item['rdfs:label']] = {
            'order': item['d3f:display-order'],
            'phases': []
        }
        print(f"Tactic: {item['rdfs:label']}")

# phases
for item in d3fend_json['@graph']:
    if 'rdfs:subClassOf' in item:
        if is_val_in_element('d3f:DefensiveTechnique', item['rdfs:subClassOf']):
            phases_ids.append(item['@id'])
            parent = id_to_label(item['d3f:enables']['@id'])
            tactics[parent]['phases'].append(item['rdfs:label'].replace(' ', '-'))
            # print(f"Tactic: {parent} \tPhase: {item['rdfs:label']}")

# sort the tactics based on the order
tactics = dict(sorted(tactics.items(), key=lambda item: item[1]['order']))
# sort the values
kill_chain_tactics = {}
for tactic, value in tactics.items():
    kill_chain_tactics[tactic] = sorted(value['phases'])


# extract all parent, child and ... techniques
seen_new = True
while seen_new:
    seen_new = False
    for item in d3fend_json['@graph']:
        if 'rdfs:subClassOf' in item:
            element = item['rdfs:subClassOf']
            if is_element_in_list(element, phases_ids) or is_element_in_list(element, techniques_ids):
                if item['@id'] in techniques_ids:
                    continue
                seen_new = True
                techniques_ids.append(item['@id'])
                if 'Memory Boundary Tracking' in item['rdfs:label']:
                    print(f"Technique: {item['rdfs:label']}")
                kill_chain = find_kill_chain_of(item)
                technique = {
                    'value': item['rdfs:label'],
                    'description': item['d3f:definition'],
                    'uuid': str(uuid.uuid5(uuid.UUID(uuid_seed), item['d3f:d3fend-id'])),
                    'meta': {
                        'kill_chain': [kill_chain],
                        'refs': [f"https://d3fend.mitre.org/technique/{item['@id']}"],
                        'external_id': item['d3f:d3fend-id']
                    }
                }
                # synonyms
                if 'd3f:synonym' in item:
                    technique['meta']['synonyms'] = get_as_list(item['d3f:synonym'])
                # relations
                if item['rdfs:label'] in relations:
                    technique['related'] = relations[item['rdfs:label']]

                cluster.append(technique)
                print(f"Technique: {item['rdfs:label']} - {item['d3f:d3fend-id']}")


cluster.save('mitre-d3fend')


try:
    galaxy = Galaxy('mitre-d3fend')
    galaxy.kill_chain_order = kill_chain_tactics
except (KeyError, FileNotFoundError):
    galaxy = Galaxy({
        'description': galaxy_description,
        'icon': "user-shield",
        'kill_chain_order': kill_chain_tactics,
        'name': galaxy_name,
        'namespace': "mitre",
        'type': galaxy_type,
        'uuid': "77d1bbfa-2982-4e0a-9238-1dae4a48c5b4",
        'version': 1
    })

galaxy.save('mitre-d3fend')

print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh.")
