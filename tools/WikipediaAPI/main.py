from modules.api import WikipediaAPI
from modules.intel import IntelAgency, Meta, Galaxy, Cluster
import os
import uuid
import json
import re

from bs4 import BeautifulSoup

CLUSTER_PATH = '../../clusters'
GALAXY_PATH = '../../galaxies'
GALAXY_NAME = 'intelligence-agencies'
UUID = str(uuid.uuid4())

def get_UUIDs():
    if GALAXY_NAME in os.listdir(CLUSTER_PATH):
        uuids = {}
        with open(os.path.join(CLUSTER_PATH, GALAXY_NAME)) as fr:
            galaxy_json = json.load(fr)
            for cluster in galaxy_json["values"]:
                uuids[cluster["value"]] = cluster["uuid"]
        return uuids
    return None

def get_notes_on_lower_level(content):
    notes = []
    for li in content.find_all('li', recursive=False):
        if li.find('ul'):
            notes.extend(get_notes_on_lower_level(li.find('ul')))
        else:
            notes.append(li.text)
    return notes

def get_agencies_from_country(heading, current_country, uuids):
    agencies = []
    content = heading.find_next('ul')
    agency_names = get_notes_on_lower_level(content)
    for name in agency_names:
        if uuids and name in uuids:
            agencies.append(IntelAgency(value=name, uuid=uuids[name], meta=Meta(country=current_country)))
        else:
            agencies.append(IntelAgency(value=name, meta=Meta(country=current_country), uuid=str(uuid.uuid4())))
    return agencies
    
def extract_info(content, uuids):
    IGNORE = ["See also", "References", "External links", "Further reading"]
    soup = BeautifulSoup(content, 'html.parser')
    agencies = []
    current_country = None
    for h2 in soup.find_all('h2'):
        span = h2.find('span', {'class': 'mw-headline'})
        if span and span.text not in IGNORE:
            current_country = span.text.strip()
            agencies.extend(get_agencies_from_country(h2, current_country, uuids))
        else:
            continue
    return agencies
    
if __name__ == '__main__':
    wiki = WikipediaAPI()
    page_title = 'List of intelligence agencies'
    content = wiki.get_page_html(page_title)
    uuids = get_UUIDs()
    if content and uuids:
        agencies = extract_info(content, uuids)
    elif not uuids:
        print(f'No UUIDs found for {GALAXY_NAME}')
        agencies = extract_info(content, None)
    else:
        print(f'Error: {content}')

    # Write to files
    galaxy = Galaxy(
        description="List of intelligence agencies",
        icon="ninja",
        name="intelligence-agencies",
        namespace="intelligence-agency",
        type="intelligence-agency",
        uuid=UUID,
        version=1,
    )
    galaxy.save_to_file(os.path.join(GALAXY_PATH, f'{GALAXY_NAME}.json'))

    cluster = Cluster(
        authors="Wikipedia",
        category="Intelligence Agencies",
        description="List of intelligence agencies",
        name="intelligence-agencies",
        source="https://en.wikipedia.org/wiki/List_of_intelligence_agencies",
        type="intelligence-agency",
        uuid=UUID,
        version=1,
    )
    for agency in agencies:
        cluster.add_value(agency)
    print(cluster.values)
    print(cluster.uuid)
    cluster.save_to_file(os.path.join(CLUSTER_PATH, f'{GALAXY_NAME}.json'))
