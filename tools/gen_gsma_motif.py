#!/usr/bin/env python3
#
#    A simple convertor of the GSMA Mobile Threat Intelligence Framework (MoTIF) Principles to a MISP Galaxy datastructure.
#    https://www.gsma.com/security/resources/fs-57-mobile-threat-intelligence-framework-motif-principles/
#    Copyright (c) 2024 MISP Project
#    Copyright (c) 2024 Christophe Vandeplas
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


import pdfplumber
import requests
import json


pdf_file_name = 'gsma-motif-principles.pdf'
pdf_url = 'https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2024/04/FS.57-MoTIF-Principles-v1.0.pdf'

# FIXME save to temporary file
# r = requests.get(pdf_url, allow_redirects=True)
# pdf_file_content = r.content

# with open(pdf_file_name, 'wb') as f:
#     f.write(pdf_file_content)

'''
- search for 4.1 Techniques and Sub-techniques Definition
- this is the start of our table parsing stuff
- each title 4.1.x is a new technique - MOTxxxx
- each title 4.1.x.y is a new sub-technique - MOTxxxx.yyy
- extract table,
-- identify if table is finishing on next page
-- if so jump to next page and merge both tables
- make generic function to convert table to dict

'''


def sub_table_to_list(table: list) -> list:
    if len(table) == 0:
        return []
    try:
        result = []
        # FIXME use header row to know column names
        for row in table:
            result.append({
                'ID': row[2].replace('\n', ''),
                'Name': row[4]. replace('\n', ' ').strip(),
                'Description': row[5]
            })
        return result
    except IndexError:
        return []


def table_to_technique(table: list) -> dict:
    '''
    Convert a table to a technique dictionary
    '''
    result = {}
    row_index = 0
    while row_index < len(table):
        row = table[row_index]

        # row[1] is None : sub-table in table
        field = cleanup_field(row[0])
        try:
            if result['ID'] == 'MOT1036.301':
                pass
        except KeyError:
            pass
        if field == 'Procedure Examples':
            # extract sub-table in the next rows
            sub_table = []
            try:
                while table[row_index + 1][0] is None:
                    sub_table.append(table[row_index + 1])
                    row_index += 1
            except IndexError:  # just the end of the page, will be handled in the next page
                pass
            value = sub_table_to_list(sub_table)
        elif field == 'Analogous technique in other frameworks':
            # column index is not always the same... so figure out the first non-empty cell
            i = 1
            value = ''
            while i < len(row):
                try:
                    if row[i] is not None:
                        value = row[i]
                        break
                except IndexError:
                    pass
                i += 1
        elif not field:
            # annoyingly a sub-table might have been parsed differently from previous page. So bad luck. There's not much we can do about it except even worse code than we have here.
            row_index += 1
            continue
        else:
            value = row[1].replace('\n', ' ').strip()

        result[field] = value

        row_index += 1

    return result


def cleanup_field(field: str) -> str:
    '''
    Cleanup a field name
    '''
    try:
        return field.strip().replace(':', '').replace('\n', ' ').replace('- ', '-').strip()
    except AttributeError:
        return ''


def is_end_of_table(table: list) -> bool:
    '''
    Check if this is the end of the table, by checking the last row in the table.
    '''
    try:
        # Techniques
        if table['ID'].startswith('MOT') and 'Analogous technique in other frameworks' in table:
            return True
        # Mitigations
        if table['ID'].startswith('MOS') and 'References' in table:
            return True

    except KeyError:
        pass
    return False


entries = {}

table_settings = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    # "explicit_vertical_lines": [],
    # "explicit_horizontal_lines": [],
    # "snap_tolerance": 6,
    "snap_x_tolerance": 6,   # pg49: must be 6
    "snap_y_tolerance": 3,   # max 14
    # "join_tolerance": 3,
    # "join_x_tolerance": 3,
    # "join_y_tolerance": 3,
    # "edge_min_length": 3,
    # "min_words_vertical": 3,
    # "min_words_horizontal": 1,
    # "intersection_tolerance": 3,
    # "intersection_x_tolerance": 3,
    # "intersection_y_tolerance": 3,
    # "text_tolerance": 3,
    # "text_x_tolerance": 3,
    # "text_y_tolerance": 3,
}

with pdfplumber.open(pdf_file_name) as pdfp:

    page_index = 0
    title_seen = False
    curr_table = None

    while page_index < len(pdfp.pages):
        page = pdfp.pages[page_index]
        # skip to section 4.1 Techniques and Sub-techniques Definition
        if not title_seen:
            page_text = page.extract_text()
            if '4.1 Techniques and Sub-techniques Definition' not in page_text or 'Table of Contents' in page_text:
                print(f"Skipping page {page_index}")
                page_index += 1
                continue
            title_seen = True

        # parse technique tables

        for table in page.extract_tables(table_settings=table_settings):
            if curr_table:   # merge tables if continuation
                # if first row does not have a first column, then it's the continuation of the previous row
                if table[0][0] == '' and table[0][1] != '':
                    curr_table[-1][1] += ' ' + table[0][1]  # add description of new row to previous row
                    table.pop(0)                            # remove the first new row of the table
                # annoyingly a sub-table might have been parsed differently from previous page. So bad luck. There's not much we can do about it except even worse code than we have here.
                # handle rest of merging case
                table = curr_table + table
                curr_table = None  # reset for clean start

            parsed_table = table_to_technique(table)
            if is_end_of_table(parsed_table):
                # valid table
                entries[parsed_table['ID']] = parsed_table
                if parsed_table['ID'] == 'MOT1565.001':
                    pass
            else:
                # incomplete table, store in curr_table and continue next row
                curr_table = table
        page_index += 1

with open('gsma_motif.json', 'w') as f:
    json.dump(entries, f, indent=4)

