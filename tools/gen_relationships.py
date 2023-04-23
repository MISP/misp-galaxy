#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#    Facilitates the creation and maintenance of relationships.
#    Copyright (C) 2022 MISP Project
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
import os
import json
import logging
import re


def relation_exists(cluster_a, cluster_b):
    """
    Checks if there is already a relationship from a to b.
    Note: you might want to run this function from a to b and from b to a.
    """
    try:
        for rel in cluster_a['related']:
            if cluster_b['uuid'] == rel['dest-uuid']:
                return True
    except KeyError:  # no relations yet
        pass
    return False


def create_relation(cluster_a, cluster_b, rel_type="similar", tags=None):
    """
    Creates unidirectional relationship, with a (optional) tags
    """
    if not relation_exists(cluster_a, cluster_b):
        rel = {"dest-uuid": cluster_b['uuid'],
               "type": rel_type}
        if tags:
            rel["tags"] = tags
        if 'related' not in cluster_a:
            cluster_a['related'] = []
        cluster_a['related'].append(rel)
        return True
    return False


class AtLeastTwoItemsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) < 2:
            parser.error('argument "{}" requires at least 2 values'.format(self.dest))
        else:
            filenames = []
            for value in values:
                if not os.path.isfile(value):
                    parser.error('file "{}" does not exist'.format(value))
                filenames.append(value)
            setattr(namespace, self.dest, filenames)


parser = argparse.ArgumentParser(description="MISP Galaxy relationship creation tool.")
parser.add_argument("files", nargs='+',
                    help="The names of the clusters. (filename or cluster-name)",
                    action=AtLeastTwoItemsAction)
parser.add_argument("-ss", "--synonyms-source",
                    help="Also use synonyms from the source cluster",
                    action='store_true')
parser.add_argument("-sd", "--synonyms-destination",
                    help="Also use synonyms from the destination cluster from which we are looking up",
                    action='store_true')
parser.add_argument("-y", "--yes",
                    help="Assume yes to all the questions, so create relationships without asking.",
                    action='store_true')
parser.add_argument('-v', '--verbose', action='count', default=0)
args = parser.parse_args()

levels = [logging.WARNING, logging.INFO, logging.DEBUG]
level = levels[min(args.verbose, len(levels) - 1)]  # cap to last level index
logging.basicConfig(level=level, format="%(message)s")

cluster_files = {}
cluster_files_changed_tracking = {}
# load all non-deprecated Clusters in memory
logging.info("Reading all non-deprecated cluster files in memory.")
for filename in args.files:
    # skip if deprecated
    galaxy_filename = os.path.join(os.path.dirname(filename), '..', 'galaxies', os.path.basename(filename))
    with open(galaxy_filename, 'r') as f:
        f_content = json.load(f)
        if f_content.get('namespace') == 'deprecated':
            logging.debug(f"Skipping file {filename} as Galaxy is deprecated.")
            continue
    # load file in memory
    logging.debug(f"Loading {filename} in memory.")
    with open(filename, 'r') as f:
        f_content = json.load(f)
        cluster_files[filename] = f_content
        cluster_files_changed_tracking[filename] = False

logging.info("Processing clusters.")
# tags by default
if args.synonyms_destination or args.synonyms_source:
    tags = ["estimative-language:likelihood-probability=\"likely\""]
else:
    tags = ["estimative-language:likelihood-probability=\"almost-certain\""]
rel_type = 'similar'
# process each cluster one by one
try:
    for cluster_filename, clusters in cluster_files.items():
        logging.debug(f"Processing cluster {cluster_filename}.")
        for cluster in clusters['values']:
            values_to_lookup = [cluster['value'].lower()]
            if args.synonyms_source:
                try:
                    values_to_lookup.extend([value.lower() for value in cluster['meta']['synonyms']])
                except KeyError:
                    pass
            for lookup_cluster_filename, lookup_clusters in cluster_files.items():
                if lookup_cluster_filename == cluster_filename:  # skip current cluster
                    continue
                for lookup_cluster in lookup_clusters['values']:
                    lookup_cluster_values = [lookup_cluster['value'].lower()]
                    if args.synonyms_destination:
                        try:
                            lookup_cluster_values.extend(
                                [value.lower() for value in lookup_cluster['meta']['synonyms']])
                        except KeyError:
                            pass
                    if any(item in values_to_lookup for item in lookup_cluster_values):
                        # we have a match from any of our source strings in the lookup cluster
                        if not relation_exists(cluster, lookup_cluster):  # no relation yet, create it
                            if args.yes:
                                logging.info(f"Found non-existing match for {cluster_filename} {values_to_lookup} in {lookup_cluster_filename} {lookup_cluster_values}. Creating it")
                                create_relationship = True
                            else:
                                # interactive prompt to ask what to do
                                print(f"Found non-existing match for {cluster_filename} {values_to_lookup} in {lookup_cluster_filename} {lookup_cluster_values}.")
                                while True:
                                    user_input = input(f"Create relation? [\u0332yes] / \u0332no / \u0332details / \u0332tags / \u0332relation: ").lower().strip()
                                    if user_input in ['yes', 'y', '']:
                                        create_relationship = True
                                        print("  creating it.")
                                        break
                                    if user_input in ['no', 'n']:
                                        create_relationship = False
                                        break
                                    if user_input in ['tags', 'tag', 't']:
                                        tags = sorted(tags)
                                        while True:
                                            print(f"Current tags: ")
                                            [print(f"  [{i}]: {t}") for i, t in enumerate(tags)]
                                            tag_input = input(f"Change tags? [\u0332no] / \u0332add / \u0332delete #: ").lower().strip()
                                            if tag_input in ['n', 'no', '']:
                                                break
                                            if tag_input.startswith('delete ') or tag_input.startswith('d '):
                                                try:
                                                    tag_delete_ids = [int(n) for n in tag_input.split(' ')[1:]]
                                                    tag_delete_ids.sort(reverse=True)
                                                    for i in tag_delete_ids:
                                                        del tags[i]
                                                except (ValueError, IndexError):
                                                    pass
                                            if tag_input in ['add', 'a']:
                                                new_tag = input("Enter tag to add: ").strip()
                                                if re.match(r'[^:]+:[^:]+="[^"]+"', new_tag) or re.match(r'[\w]+:[\w]+', new_tag):
                                                    tags.append(new_tag)
                                                else:
                                                    print("ERROR: Tag is not in the proper structure.")
                                    if user_input in ['relation', 'r']:
                                        new_relation = input(f"Current relation is '{rel_type}'. Enter new: ").lower().strip()
                                        if new_relation:
                                            rel_type = new_relation
                                    if user_input in ['details', 'd']:
                                        print("Is:")
                                        print(f"  {cluster_filename} with values: {values_to_lookup}:")
                                        print(f"    {cluster.get('description')}")
                                        print(f"{rel_type}:")
                                        print(f"  {lookup_cluster_filename} with values: {lookup_cluster_values}:")
                                        print(f"    {lookup_cluster.get('description')}")
                                        print("")
                                        print(f"Tags: {tags}")
                            if create_relationship:
                                if create_relation(cluster, lookup_cluster, rel_type=rel_type, tags=tags):
                                    cluster_files_changed_tracking[cluster_filename] = True
                                if create_relation(lookup_cluster, cluster, rel_type=rel_type, tags=tags):
                                    cluster_files_changed_tracking[lookup_cluster_filename] = True
except KeyboardInterrupt:
    print("")
    pass

# save all to file, and increment version number if something changed
for cluster_filename, changed in cluster_files_changed_tracking.items():
    if not changed:
        continue
    logging.debug(f"File {cluster_filename} has changed. Saving...")
    with open(cluster_filename, 'w') as f:
        cluster_files[cluster_filename]['version'] += 1
        json.dump(cluster_files[cluster_filename], f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write('\n')  # only needed for the beauty and to be compliant with jq_all_the_things

print("All done, please don't forget to ./jq_all_the_things.sh, commit, and then ./validate_all.sh.")
