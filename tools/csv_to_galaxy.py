#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import argparse
import uuid
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CSV to Galaxy')
    parser.add_argument("-c", "--csv", required=True, help="input csv")
    parser.add_argument("-v", "--value", type=int, required=True, help="number of the column with the value")
    parser.add_argument("-e", "--value_description", type=int, help="number of the column with description, if not defined, all other data wil be concataned")
    parser.add_argument("-w", "--version", type=int, help="version of the galaxy")
    parser.add_argument("-d", "--description", help="description of the galaxy")
    parser.add_argument("-a", "--author", help="author of the galaxy")
    parser.add_argument("-s", "--source", help="source of the galaxy")
    parser.add_argument("-t", "--type", help="type of galaxy, also the name of the generated json")
    parser.add_argument("-n", "--name", help="name of the galaxy")
    parser.add_argument("-u", "--title", action='store_true', help="set it if the first line contains the name of the columns")

    args = parser.parse_args()

    values = []
    if args.title is None:
        args.title = False

    with open(args.csv, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for data in csvreader:
            if args.title:
                args.title = False
                continue
            temp = {}
            temp["value"] = data[args.value]
            if args.value_description is not None:
                temp["description"] = data[args.value_description]
            else:
                temp["description"] = ""
                for i in range(len(data)):
                    if i != args.value and data[i] != "":
                        temp["description"] = temp["description"] + data[i] + "; "
            values.append(temp)

    galaxy = {}
    galaxy["values"] = values

    if args.version is not None:
        galaxy["version"] = args.version
    else:
        galaxy["version"] = 1

    galaxy["uuid"] = str(uuid.uuid4())

    if args.description is not None:
        galaxy["description"] = args.description
    else:
        galaxy["description"] = "automagically generated galaxy"

    if args.author is not None:
        galaxy["authors"] = [args.author]
    else:
        galaxy["authors"] = ["authorname"]

    if args.source is not None:
        galaxy["source"] = args.source
    else:
        galaxy["source"] = "source"

    if args.type is not None:
        galaxy["type"] = args.type
    else:
        galaxy["type"] = "type"

    if args.name is not None:
        galaxy["name"] = args.name
    else:
        galaxy["name"] = "name"

    print (galaxy)

    with open(args.type+'.json', 'w') as outfile:
            json.dump(galaxy, outfile)
