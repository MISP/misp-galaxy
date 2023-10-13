#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#    A simple converter of MISP galaxy cluster to asciidoctor format
#    Copyright (C) 2017 Alexandre Dulaunoy
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


import os
import json
import argparse

thisDir = os.path.dirname(__file__)

clusters = []

pathClusters = os.path.join(thisDir, '../clusters')
pathGalaxies = os.path.join(thisDir, '../galaxies')

skip_list = ["cancer.json", "handicap.json", "ammunitions.json", "firearms.json"]

for f in os.listdir(pathGalaxies):
    if '.json' in f:
        with open(os.path.join(pathGalaxies, f), 'r') as f_in:
            galaxy_data = json.load(f_in)
            if galaxy_data.get('namespace') != 'deprecated':
                if f not in skip_list:
                    clusters.append(f)

clusters.sort()

# build a mapping between uuids and Clusters
cluster_uuids = {}
for cluster in clusters:
    fullPathClusters = os.path.join(pathClusters, cluster)
    with open(fullPathClusters) as fp:
        c = json.load(fp)
    for v in c['values']:
        if 'uuid' not in v:
            continue
        cluster_uuids[v['uuid']] = 'misp-galaxy:{}="{}"'.format(c['type'], v['value'])


argParser = argparse.ArgumentParser(description='Generate documentation from MISP galaxy clusters', epilog='Available galaxy clusters are {0}'.format(clusters))
argParser.add_argument('-v', action='store_true', help='Verbose mode')
args = argParser.parse_args()

def header():
    doc = []
    dedication = "\n[dedication]\n== Funding and Support\nThe MISP project is financially and resource supported by https://www.circl.lu/[CIRCL Computer Incident Response Center Luxembourg ].\n\nimage:{images-misp}logo.png[CIRCL logo]\n\nA CEF (Connecting Europe Facility) funding under CEF-TC-2016-3 - Cyber Security has been granted from 1st September 2017 until 31th August 2019 as ***Improving MISP as building blocks for next-generation information sharing***.\n\nimage:{images-misp}en_cef.png[CEF funding]\n\nIf you are interested to co-fund projects around MISP, feel free to get in touch with us.\n\n"
    doc += ":toc: right\n"
    doc += ":toclevels: 1\n"
    doc += ":toc-title: MISP Galaxy Cluster\n"
    doc += ":icons: font\n"
    doc += ":sectanchors:\n"
    doc += ":sectlinks:\n"
    doc += ":images-cdn: https://raw.githubusercontent.com/MISP/MISP/2.4/INSTALL/logos/\n"
    doc += ":images-misp: https://www.misp-project.org/assets/images/\n"
    doc += "\n= MISP Galaxy Clusters\n\n"
    doc += "= Introduction\n"
    doc += "\nimage::{images-cdn}misp-logo.png[MISP logo]\n\n"
    doc += "The MISP threat sharing platform is a free and open source software helping information sharing of threat intelligence including cyber security indicators, financial fraud or counter-terrorism information. The MISP project includes multiple sub-projects to support the operational requirements of analysts and improve the overall quality of information shared.\n\n"
    doc += ""
    doc += "\nMISP galaxy is a simple method to express a large object called cluster that can be attached to MISP events or attributes. A cluster can be composed of one or more elements. Elements are expressed as key-values. There are default vocabularies available in MISP galaxy but those can be overwritten, replaced or updated as you wish.  Existing clusters and vocabularies can be used as-is or as a template. MISP distribution can be applied to each cluster to permit a limited or broader distribution scheme.\n"
    doc += "The following document is generated from the machine-readable JSON describing the https://github.com/MISP/misp-galaxy[MISP galaxy]."
    doc += "\n\n"
    doc += "<<<\n"
    doc += dedication
    doc += "<<<\n"
    doc += "= MISP galaxy\n"
    return doc


def asciidoc(content=False, t='title', title='', typename='', uuid=None):
    adoc = []
    adoc += "\n"
    output = ""
    if t == 'title':
        output = '== ' + content
    elif t == 'info':
        output = "\n{}.\n\n{} {} {}$${}$$.json[*this location*] {}.\n".format(content, 'NOTE: ', title, 'is a cluster galaxy available in JSON format at https://github.com/MISP/misp-galaxy/blob/master/clusters/', typename.lower(), ' The JSON format can be freely reused in your application or automatically enabled in https://www.github.com/MISP/MISP[MISP]')
    elif t == 'author':
        output = '\nauthors:: {}\n'.format(' - '.join(content))
    elif t == 'value':
        output = '=== {}'.format(content)
    elif t == 'description':
        output = '\n{}\n'.format(content)
    elif t == 'meta-synonyms':
        if 'synonyms' in content:
            for s in content['synonyms']:
                output = "{}\n* {}\n".format(output, s)
            output = '{} is also known as:\n{}\n'.format(title, output)
    elif t == 'meta-refs':
        if 'refs' in content:
            output = '{}{}'.format(output, '\n.Table References\n|===\n|Links\n')
            for r in content['refs']:
                output = '{}|{}[{}]\n'.format(output, r, r)
            output = '{}{}'.format(output, '|===\n')
    elif t == 'related':
        for r in content:
            try:
                output = "{}\n* {}: {} with {}\n".format(output, r['type'], cluster_uuids[r['dest-uuid']], ', '.join(r['tags']))
            except Exception:
                pass  # ignore lookup errors
        if output:
            output = '{} has relationships with:\n{}\n'.format(title, output)
            output = '\nlink:https://www.misp-project.org/graphs/{}.png[View relationships graph]\n\n{}\n'.format(uuid, output)
    adoc += output
    return adoc


adoc = []
adoc += header()

for cluster in clusters:
    fullPathClusters = os.path.join(pathClusters, cluster)
    with open(fullPathClusters) as fp:
        c = json.load(fp)
    title = c['name']
    typename = c['type']
    adoc += asciidoc(content=title, t='title')
    adoc += asciidoc(content=c['description'], t='info', title=title, typename=typename)
    if 'authors' in c:
        adoc += asciidoc(content=c['authors'], t='author', title=title)
    for v in c['values']:
        adoc += asciidoc(content=v['value'], t='value')
        if 'description' in v:
            adoc += asciidoc(content=v['description'], t='description')
        adoc += asciidoc(content='The tag is: _misp-galaxy:{}="{}"_'.format(c['type'], v['value']), t='description')
        if 'meta' in v:
            adoc += asciidoc(content=v['meta'], t='meta-synonyms', title=v['value'])
        if 'related' in v:
            adoc += asciidoc(content=v['related'], t='related', title=v['value'], uuid=v['uuid'])
        if 'meta' in v:
            adoc += asciidoc(content=v['meta'], t='meta-refs', title=v['value'])
print(''.join(adoc))
