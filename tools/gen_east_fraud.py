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

url = 'https://www.association-secure-transactions.eu/industry-information/fraud-definitions/'
techniques = []


def write_file(self, fname, file_data):
    with open(fname, 'w') as f:
        json.dump(file_data, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write('\n')


try:
    response = requests.get(url, timeout=3)
except Exception:
    exit("ERROR: Could not download the webpage. Are you sure you have internet connectivity?")

soup = BeautifulSoup(response.content, 'lxml')
entry_content = soup.find('div', class_='entry-content')
t_first = entry_content.find('table')
p_start = t_first.find_previous_sibling()
# for sibling in
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
            # print(f' {k.text}: {v.text}')
            print(f'{category} - {sub_category} - {k.text}')
print("ERROR : This program is not ready yet. Please ignore.")