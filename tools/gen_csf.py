#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    A simple convertor script to generate galaxies from the MITRE NICE framework
#    https://niccs.cisa.gov/workforce-development/nice-framework
#    Copyright (C) 2024 Jean-Louis Huynen
#    Copyright (C) 2024 Déborah Servili
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

import pdb
import requests
import json
import os
import uuid
import re
from bs4 import BeautifulSoup

# uuidv4 generated to be concatenated in v5: 43803a9f-9ea6-4ebc-9cb5-68ccdc2c23e0

galaxy = {
    "namespace": "first",
    "type": "first-csirt-services-framework",
    "name": "FIRST CSIRT Services Framework",
    "description": "The Computer Security Incident Response Team (CSIRT) Services Framework is a high-level document describing in a structured way a collection of cyber security services and associated functions that Computer Security Incident Response Teams and other teams providing incident management related services may provide",
    "uuid": "4a72488f-ef5b-4895-a5d9-c625dee663cb",
    "version": 1,
    "icon": 'user',
}

cluster = {
    'authors': ["FIRST", "CIRCL", "Jean-Louis Huynen"],
    'category': 'csirt',
    "type": "first-csirt-services-framework",
    "name": "FIRST CSIRT Services Framework",
    "description": "The Computer Security Incident Response Team (CSIRT) Services Framework is a high-level document describing in a structured way a collection of cyber security services and associated functions that Computer Security Incident Response Teams and other teams providing incident management related services may provide",
    "uuid": "4a72488f-ef5b-4895-a5d9-c625dee663cb",
    'source': 'https://www.first.org/standards/frameworks/csirts/csirt_services_framework_v2.1',
    'values': [],
    'version': 1,
}

# URL to download
url = "https://www.first.org/standards/frameworks/csirts/csirt_services_framework_v2.1#5-Service-Area-Information-Security-Event-Management"

# Send a GET request to the webpage
response = requests.get(url)

def extract_nostrong_content(element):
    content = element.find_next_siblings('p', limit=3)
    extracted = {}

    extracted["purpose"] = content[0].text.strip()[8:]
    for sibling in content[0].find_next_siblings():
        if "Description:" in sibling.text:
            break
        extracted["purpose"] += f" {sibling.text.strip()}"

    extracted["description"] = content[1].text.strip()[12:]
    for sibling in content[1].find_next_siblings():
        if "Outcome:" in sibling.text:
            break
        extracted["description"] += f" {sibling.text.strip()}"

    extracted["outcome"] = content[2].text.strip()[8:]
    for sibling in content[2].find_next_siblings():
        if sibling.name in ["h2", "h3", "h4"] or any(substring in sibling.text for substring in ["The following functions", "List of functions"]):
            break
        extracted["outcome"] += f" {sibling.text.strip()}"
    return extracted

def extract_content(element):
    content = {}
    description_title = element.find_next(
        "em", string=lambda text: "Description:" in text
    )
    purpose_title = element.find_next("em", string=lambda text: "Purpose:" in text)
    outcome_title = element.find_next("em", string=lambda text: "Outcome:" in text)

    content["purpose"] = (
        purpose_title.parent.parent.get_text(strip=True).replace("Purpose:", "").strip()
    )
    for sibling in purpose_title.parent.parent.find_next_siblings():
        if "Description:" in sibling.text:
            break
        content["purpose"] += f" {sibling.text.strip()}"

    content["description"] = (
        description_title.parent.parent.get_text(strip=True)
        .replace("Description:", "")
        .strip()
    )

    for sibling in description_title.parent.parent.find_next_siblings():
        if "Outcome:" in sibling.text:
            break
        content["description"] += f" {sibling.text.strip()}"

    content["outcome"] = (
        outcome_title.parent.parent.get_text(strip=True).replace("Outcome:", "").strip()
    )
    for sibling in outcome_title.parent.parent.find_next_siblings():
        if sibling.name in ["h2", "h3", "h4"] or any(substring in sibling.text for substring in ["The following functions", "List of functions"]):
            break
        content["outcome"] += f" {sibling.text.strip()}"
        content["outcome"] = content["outcome"].split("The following functions")[0].strip()
    return content


def remove_heading(input_string):
    return re.sub(r'^\d+(\.\d+)*\s+', '', input_string)

# Check if the request was successful
if response.status_code == 200:
    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Removing all links <a>
    for a in soup.find_all('a', href=True):
        if a['href'].startswith('#'):
            a.decompose()

    # Extract the section titled "4 CSIRT Services Framework Structure"
    section_header = soup.find(
        'h2', id="5-Service-Area-Information-Security-Event-Management"
    )
    if section_header:

        services = section_header.find_next_siblings('h3')
        functions = section_header.find_next_siblings('h4')

        for service in services:
            if "Monitoring and detection" in service.text:
                content = extract_nostrong_content(service)
            else:
                content = extract_content(service)
            name = remove_heading(service.text.strip())
            suuid = str(
                uuid.uuid5(uuid.UUID("43803a9f-9ea6-4ebc-9cb5-68ccdc2c23e0"), name)
            )
            cluster["values"].append(
                {
                    "description": content["description"],
                    "meta": {
                        "purpose": content["purpose"],
                        "outcome": content["outcome"],
                    },
                    "uuid": suuid,
                    "value": name,
                    "related": [],
                }
            )

        for function in functions:
            content = extract_content(function)
            # get the parent service
            parent_service = function.find_previous('h3')
            relationship = {
                "dest-uuid": str(
                    uuid.uuid5(
                        uuid.UUID("43803a9f-9ea6-4ebc-9cb5-68ccdc2c23e0"),
                        remove_heading(parent_service.text.strip()),
                    )
                ),
                "type": "part-of",
            }

            name = remove_heading(function.text.strip())

            cluster["values"].append(
                {
                    "description": content["description"],
                    "meta": {
                        "purpose": content["purpose"],
                        "outcome": content["outcome"],
                    },
                    "uuid": str(
                        uuid.uuid5(
                            uuid.UUID("43803a9f-9ea6-4ebc-9cb5-68ccdc2c23e0"), name
                        )
                    ),
                    "value": name,
                    "related": [relationship],
                }
            )

        with open(
            os.path.join(
                os.path.dirname(__file__),
                '..',
                'galaxies',
                f'first-csirt-services-framework.json',
            ),
            'w',
        ) as f:
            json.dump(galaxy, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write(
                '\n'
            )  # only needed for the beauty and to be compliant with jq_all_the_things

        with open(
            os.path.join(
                os.path.dirname(__file__),
                '..',
                'clusters',
                f'first-csirt-services-framework.json',
            ),
            'w',
        ) as f:
            json.dump(cluster, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write(
                '\n'
            )  # only needed for the beauty and to be compliant with jq_all_the_things

    else:
        print("Couldn't find the section header.")
else:
    print(f"Failed to download the webpage. Status code: {response.status_code}")
