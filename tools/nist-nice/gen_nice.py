#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    A simple convertor script to generate galaxies from the MITRE NICE framework
#    https://niccs.cisa.gov/workforce-development/nice-framework
#    Copyright (C) 2024 Jean-Louis Huynen
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

import argparse
import json
import os
import uuid
import csv

# uuidv4 generated to be concatenated in v5: 1d348708-7cd8-4854-9eac-f93c0dab8cdd

parser = argparse.ArgumentParser(
    description='Create/update the NICE Framework Taxonomies based on the NICE Framework json file.'
)
parser.add_argument(
    "-p", "--path", required=True, help="Path to the NICE Framework json file"
)

args = parser.parse_args()

if not os.path.exists(args.path):
    exit("ERROR: path incorrect")

if not os.path.exists(os.path.join(os.path.dirname(__file__), "cybersecurity-opm.csv")):
    exit("ERROR: cannot find opm file")


# create OPM description from OPM csv file as this data is missing from the NICE framework
with open(
    os.path.join(os.path.dirname(__file__), "cybersecurity-opm.csv"), newline=''
) as csvfile:
    opm = {}
    reader = csv.reader(csvfile, delimiter=',', quotechar="\"")
    for row in reader:
        opm[row[0]] = row[1]


g = ["work_role", "skill", "task", "knowledge", "competency_area", "opm_code"]

galaxies = {
    "work_role": {
        "namespace": "nist-nice",
        "type": "nice-framework-work_roles",
        "name": "NICE Work Roles",
        "description": "Work roles based on the NIST NICE framework",
        "uuid": "10a2e9d7-781b-4ff4-bb3e-f0003108fe41",
        "version": 1,
        "icon": 'user',
    },
    "skill": {
        "namespace": "nist-nice",
        "type": "nice-framework-skills",
        "name": "NICE Skills",
        "description": "Skills based on the NIST NICE framework",
        "uuid": "96c5b9e7-5e70-479e-990c-8f1dea06c520",
        "version": 1,
        "icon": 'user',
    },
    "task": {
        "namespace": "nist-nice",
        "type": "nice-framework-tasks",
        "name": "NICE Tasks",
        "description": "Tasks based on the NIST NICE framework",
        "uuid": "98ba1aa3-d171-49e4-adf1-b7fb5e26a942",
        "version": 1,
        "icon": 'user',
    },
    "knowledge": {
        "namespace": "nist-nice",
        "type": "nice-framework-knowledges",
        "name": "NICE Knowledges",
        "description": "Knowledge based on the NIST NICE framework",
        "uuid": "de7e23f2-cef8-44ed-b209-b584f7da58a2",
        "version": 1,
        "icon": 'user',
    },
    "competency_area": {
        "namespace": "nist-nice",
        "type": "nice-framework-competency_areas",
        "name": "NICE Competency areas",
        "description": "Competency areas based on the NIST NICE framework",
        "uuid": "e78357aa-01bd-4635-99a1-8eb860fa3bd5",
        "version": 1,
        "icon": 'user',
    },
    "opm_code": {
        "namespace": "nist-nice",
        "type": "nice-framework-opm_codes",
        "name": "OPM codes in cybersecurity",
        "description": "Office of Personnel Management codes in cybersecurity",
        "uuid": "2c56dfbc-82a5-48db-aea4-854ede951c65",
        "version": 1,
        "icon": 'user',
    },
}

clusters = {
    "work_role": {
        'authors': ["NIST", "Jean-Louis Huynen"],
        'category': 'workforce',
        "type": "nice-framework-work_roles",
        "name": "NICE Work Roles",
        "description": "Work roles based on the NIST NICE framework",
        "uuid": "f81819e1-326b-41a5-89dd-a40d73c5bbbf",
        'source': '',
        'values': [],
        'version': 1,
    },
    "skill": {
        'authors': ["NIST", "Jean-Louis Huynen"],
        'category': 'workforce',
        "type": "nice-framework-skills",
        "name": "NICE Skills",
        "description": "Skills based on the NIST NICE framework",
        "uuid": "2d330f93-fa49-4451-859a-aacc68c63110",
        'source': '',
        'values': [],
        'version': 1,
    },
    "task": {
        'authors': ["NIST", "Jean-Louis Huynen"],
        'category': 'workforce',
        "type": "nice-framework-tasks",
        "name": "NICE Tasks",
        "description": "Tasks based on the NIST NICE framework",
        "uuid": "6bcf78de-a3fb-4636-90bc-95a86817ad65",
        'source': '',
        'values': [],
        'version': 1,
    },
    "knowledge": {
        'authors': ["NIST", "Jean-Louis Huynen"],
        'category': 'workforce',
        "type": "nice-framework-knowledges",
        "name": "NICE Knowledges",
        "description": "Knowledge based on the NIST NICE framework",
        "uuid": "796e3e82-ca9a-4749-8421-4810ed440755",
        'source': '',
        'values': [],
        'version': 1,
    },
    "competency_area": {
        'authors': ["NIST", "Jean-Louis Huynen"],
        'category': 'workforce',
        "type": "nice-framework-competency_areas",
        "name": "NICE Competency areas",
        "description": "Competency areas based on the NIST NICE framework",
        "uuid": "91696bc7-ede9-4875-8814-768bd5c99c66",
        'source': '',
        'values': [],
        'version': 1,
    },
    "opm_code": {
        'authors': ["OPM", "Jean-Louis Huynen"],
        'category': 'workforce',
        "type": "nice-framework-opm_codes",
        "name": "OPM codes in cybersecurity",
        "description": "Office of Personnel Management codes in cybersecurity",
        "uuid": "76772dae-0e98-4d96-8603-6993aea936d1",
        'source': 'https://dw.opm.gov/datastandards/referenceData/2273/current',
        'values': [],
        'version': 1,
    },
}


def get_relationships(nice_data, external_id):
    relationships = []
    for element in nice_data["response"]["elements"]["relationships"]:
        if element["source_element_identifier"] == external_id:
            relationships.append(
                {
                    "dest-uuid": str(
                        uuid.uuid5(
                            uuid.UUID("1d348708-7cd8-4854-9eac-f93c0dab8cdd"),
                            element["dest_element_identifier"],
                        )
                    ),
                    "type": "involves",
                }
            )

    return relationships


with open(args.path) as f:
    # loading NICE json file
    nice_data = json.load(f)

    # relationship counter
    ctr_rel = 0

    # populate clusters' source
    source = nice_data["response"]["elements"]["documents"]
    for e in g:
        if e != "opm_code":
            clusters[e]["source"] = source[0]["website"]

    # Populate the clusters' values
    for element in nice_data["response"]["elements"]["elements"]:

        # Defining a uuidd v5 identifier
        uuid_str = str(
            uuid.uuid5(
                uuid.UUID("1d348708-7cd8-4854-9eac-f93c0dab8cdd"),
                element["element_identifier"],
            )
        )

        # generating relationship
        relationships = get_relationships(nice_data, element["element_identifier"])
        if relationships != []:
            ctr_rel = ctr_rel + len(relationships)

        # Adding values in corresponding cluster
        if element["element_type"] in g:
            if element["element_type"] == "opm_code":
                clusters[element["element_type"]]["values"].append(
                    {
                        "description": opm[element["element_identifier"]],
                        "uuid": uuid_str,
                        "value": f'{opm[element["element_identifier"]][0:150]} - {element["element_identifier"]}',
                        "related": relationships,
                    }
                )
            else:
                clusters[element["element_type"]]["values"].append(
                    {
                        "description": element["text"],
                        "uuid": uuid_str,
                        "value": element["element_identifier"],
                        "value": f'{element["text"][0:150]} - {element["element_identifier"]}',
                        "related": relationships,
                    }
                )

# Writing galaxies and clusters
for e in g:
    with open(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'galaxies',
            f'nice-framework-{e}s.json',
        ),
        'w',
    ) as f:
        json.dump(galaxies[e], f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write(
            '\n'
        )  # only needed for the beauty and to be compliant with jq_all_the_things

    with open(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'clusters',
            f'nice-framework-{e}s.json',
        ),
        'w',
    ) as f:
        json.dump(clusters[e], f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write(
            '\n'
        )  # only needed for the beauty and to be compliant with jq_all_the_things

print(f'{len(g)*2} file created:')
for e in g:
    print(f'- nice-framework-{e}s.json contains {len(clusters[e]["values"])} elements')
print(f' -{ctr_rel} relationships were created')
