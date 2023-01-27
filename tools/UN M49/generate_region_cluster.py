#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from uuid import uuid4

current_path = Path(__file__).resolve().parent


def _generate_cluster_values(cluster_values: dict):
    values = []
    for _, cluster_value in sorted(cluster_values.items()):
        values.append(cluster_value)
    return values


def _parse_csv_input(input_file: Path) -> dict:
    # We create a mapping to associate the regions and their sub-regions
    regions_mapping = defaultdict(set)
    with open(input_file, 'rt', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            '''
            gc: Global Code
            gn: Global Name
            rc: Region Code
            rn: Region Name
            src: Sub-region Code
            srn: Sub-region Name
            irc: Intermediate Region Code
            irn: Intermediate Region Name
            mc: M49 Code
            coa: Country of Area
            '''
            gc, gn, rc, rn, src, srn, irc, irn, mc, coa, *_ = row

            global_region = f'{gc} - {gn}'
            if rc and rn:
                # Almost all the areas have a region information
                region = f'{rc} - {rn}'
                regions_mapping[global_region].add(region)
                # Deal with the region information
                sub_region = f'{src} - {srn}'
                regions_mapping[region].add(sub_region)
                country = f'{mc} - {coa}'
                if irc and irn:
                    # If the country is located in an intermediate region
                    inter_region = f'{irc} - {irn}'
                    # Deal with the sub-region information
                    regions_mapping[sub_region].add(inter_region)
                    # Deal with the intermediate region information
                    regions_mapping[inter_region].add(country)
                else:
                    # The country is located in a sub-region
                    regions_mapping[sub_region].add(country)
            else:
                # Should be only Antarctica which has only global region and
                # country information
                country = f'{mc} - {coa}'
                regions_mapping[global_region].add(country)
                regions_mapping[country] = None
    return regions_mapping


def update_cluster(input_file, filename):
    with open(filename, 'rt', encoding='utf-8') as f:
        region_cluster = json.load(f)
    cluster = {value['value']: value for value in region_cluster['values']}
    regions_mapping = _parse_csv_input(input_file)
    is_changed = False
    for region, subregions in regions_mapping.items():
        if region not in cluster:
            cluster_value = {
                'value': region,
                'uuid': uuid4().__str__(),
            }
            if subregions is not None:
                cluster_value['meta'] = {
                    'subregions': sorted(subregions)
                }
            cluster[region] = cluster_value
            is_changed = True
        else:
            if subregions != cluster[region].get('meta', {}).get('subregions'):
                if subregions is not None:
                    cluster[region]['meta'] = {
                        'subregions': sorted(subregions)
                    }
                is_changed = True
    if is_changed:
        region_cluster['values'] = _generate_cluster_values(cluster)
        with open(filename, 'wt', encoding='utf-8') as f:
            f.write(json.dumps(region_cluster, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates/updates the region galaxy cluster')
    parser.add_argument(
        '-i', '--input', type=Path, default=current_path / 'UNSD.csv',
        help="CSV input file"
    )
    args = parser.parse_args()

    filename = current_path.parents[1] / 'clusters' / 'region.json'
    update_cluster(args.input, filename)
