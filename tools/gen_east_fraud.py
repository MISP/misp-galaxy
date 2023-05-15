#!/usr/bin/env python3
#
#    A simple convertor of the E.A.S.T. Fraud definitions to a MISP Galaxy datastructure.
#    https://www.association-secure-transactions.eu/industry-information/fraud-definitions/
#    Copyright (c) 2023 MISP Project
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

from bs4 import BeautifulSoup
import json
import requests
import string
import uuid
import os

url = 'https://www.association-secure-transactions.eu/industry-information/fraud-definitions/'

try:
    response = requests.get(url, timeout=3)
except Exception:
    exit("ERROR: Could not download the webpage. Are you sure you have internet connectivity?")

with open(os.path.join('..', 'galaxies', 'attck4fraud.json'), 'r') as f:
    tactics_options = json.load(f)['kill_chain_order']['fraud-tactics']

with open(os.path.join('..', 'clusters', 'attck4fraud.json'), 'r') as f:
    json_data = json.load(f)
# build value/synonym based mapping to UUID allowing us to lookup what exists
mapping = {}
for cluster in json_data['values']:
    mapping[cluster['value'].lower()] = cluster['uuid']
    try:
        for synonym in cluster['meta']['synonyms']:
            mapping[synonym.lower()] = cluster['uuid']
    except KeyError:
        pass

changed = False
soup = BeautifulSoup(response.content, 'lxml')
entry_content = soup.find('div', class_='entry-content')
t_first = entry_content.find('table')
p_start = t_first.find_previous_sibling()
for child in entry_content.children:
    if 'p' == child.name and child.find('strong'):
        # new category
        category = string.capwords(child.text)
    elif 'table' == child.name:
        # new sub-category with entries to parse
        sub_category = string.capwords(child.find('th').text.split('\n')[0])
        # print(f'{category} - {sub_category}')
        for tr in child.find_all('tr'):
            try:
                k, v = tr.find_all('td')
            except ValueError:
                continue  # skip header row
            value = k.text.strip()
            description = v.text.strip()
            # check by value or synonym if cluster is already known, and skip known
            existing_uuid = mapping.get(value.lower())
            if existing_uuid:
                print(f'{category} # {sub_category} # {value} is already known as {existing_uuid}')
                continue
            # prompt as for a new cluster meta kill_chain is not known
            print('Found new record:')
            print(f'  {category} # {sub_category} # {value} # {description}')
            while True:
                tactic = input(f'What is the right fraud-tactic? options are {tactics_options}\n> ')
                if tactic.strip() in tactics_options:
                    tactic = tactic.strip()
                    break
                elif any(option.startswith(tactic.strip()) for option in tactics_options):
                    for option in tactics_options:
                        if option.startswith(tactic.strip()):
                            tactic = option
                            print(f'Chosen: {tactic}')
                            found = True
                            break
                    break
                else:
                    print("Given option is not in the list. Please input again.")

            cluster = {
                'value': value,
                'description': description,
                'uuid': str(uuid.uuid5(uuid.UUID("9319371e-2504-4128-8410-3741cebbcfd3"), value)),
                'meta': {
                    'refs': ['https://www.association-secure-transactions.eu/industry-information/fraud-definitions/'],
                    'kill_chain': [f'fraud-tactics:{tactic}'],
                }
            }
            json_data['values'].append(cluster)
            changed = True

if changed:
    json_data['version'] += 1
    with open(os.path.join('..', 'clusters', 'attck4fraud.json'), 'w') as f:
        json.dump(json_data, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write('\n')

print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh.")
