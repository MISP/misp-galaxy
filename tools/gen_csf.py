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
    "icon": 'user'
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
    'version': 1 
}

# URL to download
url = "https://www.first.org/standards/frameworks/csirts/csirt_services_framework_v2.1#5-Service-Area-Information-Security-Event-Management"

# Send a GET request to the webpage
response = requests.get(url)

def extract_text(element):
    content = element.find_next_siblings('p', limit=3)
    content_text = ""
    for i, elm in enumerate(content):
        if i !=0 :
            content_text += "\n" + elm.text.strip()
        else:
            content_text += elm.text.strip()
    return content_text

def remove_heading(input_string):
    return re.sub(r'^\d+(\.\d+)*\s+', '', input_string)

# Check if the request was successful
if response.status_code == 200:
    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the section titled "4 CSIRT Services Framework Structure"
    section_header = soup.find('h2', id="5-Service-Area-Information-Security-Event-Management")
    if section_header:

        services = section_header.find_next_siblings('h3')
        functions = section_header.find_next_siblings('h4')

        for service in services:
            name = remove_heading(service.text.strip())
            suuid = str(uuid.uuid5(uuid.UUID("43803a9f-9ea6-4ebc-9cb5-68ccdc2c23e0"), name))
            cluster["values"].append(
                {
                    "description": extract_text(service),
                    "uuid" : suuid,
                    "value": name,
                    "related": []
                }
            )

        for function in functions:
            # get the parent service
            parent_service = function.find_previous('h3')
            relationship = {
                "dest-uuid": str(uuid.uuid5(uuid.UUID("43803a9f-9ea6-4ebc-9cb5-68ccdc2c23e0"), remove_heading(parent_service.text.strip()))),
                "type": "used-by"
            }

            name = remove_heading(function.text.strip())

            cluster["values"].append(
                {
                    "description": extract_text(function),
                    "uuid" : str(uuid.uuid5(uuid.UUID("43803a9f-9ea6-4ebc-9cb5-68ccdc2c23e0"), name)),
                    "value": name,
                    "related": [relationship]
                }
            )
    
        with open(os.path.join(os.path.dirname(__file__), '..', 'galaxies', f'first-csirt-services-framework.json'), 'w') as f:
            json.dump(galaxy, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things

        with open(os.path.join(os.path.dirname(__file__), '..', 'clusters', f'first-csirt-services-framework.json'), 'w') as f:
            json.dump(cluster, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things

    else:
        print("Couldn't find the section header.")
else:
    print(f"Failed to download the webpage. Status code: {response.status_code}")
