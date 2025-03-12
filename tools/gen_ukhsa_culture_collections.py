#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    A simple convertor of the UK Health Security Agency Culture Collections
#    to a MISP Galaxy datastructure.
#    Copyright (C) 2024 MISP Project
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


import json
import requests
import uuid
from pymispgalaxies import Cluster, Galaxy

'''
From https://www.culturecollections.org.uk/search/?searchScope=Product&pageNumber=1&filter.collectionGroup=0&filter.collection=0&filter.sorting=DateCreated
JSON is loaded, needs to be paginated

Culturecollections.org.uk is published under the Open Government Licence, allowing the reproduction of information as
long as the license terms are obeyed. Material on this website is subject to Crown copyright protection unless otherwise
indicated. Users should be aware that information provided to third parties through feeds may be edited or cached, and
we do not guarantee the accuracy of such third-party products.
https://www.culturecollections.org.uk/training-and-support/policies/terms-and-conditions-of-use/

The Culture Collections represent deposits of cultures from world-wide sources. While every effort is made to ensure
details distributed by Culture Collections are accurate, Culture Collections cannot be held responsible for any
inaccuracies in the data supplied. References where quoted are mainly attributed to the establishment of the cell
culture and not for any specific property of the cell line, therefore further references should be obtained regarding
cell culture characteristics. Passage numbers where given act only as a guide and Culture Collections does not guarantee
the passage number stated will be the passage number received by the customer.
'''


def download_items():
    data = {'items': [],
            'collections': {},
            'collection_groups': {}}
    page_number = 1
    page_number_max = None
    while True:
        url = 'https://www.culturecollections.org.uk/umbraco/api/searchApi/getSearchResults?searchParams={"searchText":"","searchScope":"Product","pageNumber":' + str(page_number) + ',"filter":{"collectionGroup":"0","collection":"0","facets":{},"sorting":"DateCreated"}}'
        page_resp = requests.get(url)
        page_resp.encoding = 'utf-8-sig'
        page_data = page_resp.json()
        page_number_max = page_data['pagination']['totalPages']

        for c in page_data['filter']['collections']['aggregationItems']:
            data['collections'][int(c['value'])] = c['title']
        for cg in page_data['filter']['collectionGroups']['aggregationItems']:
            data['collection_groups'][int(cg['value'])] = cg['title']
        for item in page_data['items']:
            item['collection'] = data['collections'][item['collectionId']]
        data['items'].extend(page_data['items'])
        print(f"Fetching page {page_number}/{page_number_max}: ", end="")
        print(f"items size is now {len(data['items'])} as I extended with {len(page_data['items'])} items.")
        if page_number >= page_number_max:
            break
        page_number += 1
    return data


def save_items(d):
    with open('items.json', 'w') as f:
        json.dump(d, f, indent=2, sort_keys=True)
    return True


def load_saved_items():
    with open('items.json', 'r') as f:
        d = json.load(f)
    return d


data = download_items()
# save_items(data)
# data = load_saved_items()

clusters_dict = {}
for item in data['items']:
    # create a cluster
    cluster = {
        'value': f"{item['name']}",
        'uuid': str(uuid.uuid5(uuid.UUID("bbe11c06-1d6a-477e-88f1-cdda2d71de56"), item['name'])),
        'meta': {
            'refs': [item['url']],
            'external_id': [item['catalogueNumber']]
        }
    }
    # add all properties of the culture
    for p in item['properties']:
        if p['value']:
            p_name = p['name'].lower().replace(' ', '_')
            if p['name'] not in cluster['meta']:
                cluster['meta'][p_name] = []
            cluster['meta'][p_name].append(p['value'])
    # merge if the collection already exists
    if cluster['value'] in clusters_dict:
        clusters_dict[cluster['value']]['meta']['refs'].extend(cluster['meta']['refs'])
        clusters_dict[cluster['value']]['meta']['external_id'].extend(cluster['meta']['external_id'])
    else:
        clusters_dict[cluster['value']] = cluster

# transform dict to list
cluster = Cluster('ukhsa-culture-collections', skip_duplicates=True)
cluster.cluster_values = {}
for item in clusters_dict.values():
    cluster.append(item, skip_duplicates=True)
cluster.save('ukhsa-culture-collections')

for cluster, duplicate in cluster.duplicates:
    print(f"WARNING: Skipped duplicate: {duplicate} in cluster {cluster}")

try:
    galaxy = Galaxy('ukhsa-culture-collections')
except KeyError:
    galaxy = Galaxy({
        'icon': "virus",
        'name': "UKHSA Culture Collections",
        'description': "UK Health Security Agency Culture Collections represent deposits of cultures that consist of expertly preserved, authenticated cell lines and microbial strains of known provenance.",
        'namespace': "gov.uk",
        'type': "ukhsa-culture-collections",
        'uuid': "bbe11c06-1d6a-477e-88f1-cdda2d71de56",
        'version': 1
    })
galaxy.save('ukhsa-culture-collections')

print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh.")
