#!/usr/bin/env python
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

for f in os.listdir(pathClusters):
    if '.json' in f:
        clusters.append(f)

clusters.sort()

argParser = argparse.ArgumentParser(description='Generate documentation from MISP galaxy clusters', epilog='Available galaxy clusters are {0}'.format(clusters))
argParser.add_argument('-v', action='store_true', help='Verbose mode')
args = argParser.parse_args()

def header(adoc=False):
    if adoc is False:
        return False

    dedication = "\n[dedication]\n== Funding and Support\nThe MISP project is financially and resource supported by https://www.circl.lu/[CIRCL Computer Incident Response Center Luxembourg ].\n\nimage:{images-misp}logo.png[CIRCL logo]\n\nA CEF (Connecting Europe Facility) funding under CEF-TC-2016-3 - Cyber Security has been granted from 1st September 2017 until 31th August 2019 as ***Improving MISP as building blocks for next-generation information sharing***.\n\nimage:{images-misp}en_cef.png[CEF funding]\n\nIf you are interested to co-fund projects around MISP, feel free to get in touch with us.\n\n"
    doc = adoc
    doc = doc + ":toc: right\n"
    doc = doc + ":toclevels: 1\n"
    doc = doc + ":toc-title: MISP Galaxy Cluster\n"
    doc = doc + ":icons: font\n"
    doc = doc + ":sectanchors:\n"
    doc = doc + ":sectlinks:\n"
    doc = doc + ":images-cdn: https://raw.githubusercontent.com/MISP/MISP/2.4/INSTALL/logos/\n"
    doc = doc + ":images-misp: https://www.misp-project.org/assets/images/\n"
    doc = doc + "\n= MISP Galaxy Clusters\n\n"
    doc = doc + "= Introduction\n"
    doc = doc + "\nimage::{images-cdn}misp-logo.png[MISP logo]\n\n"
    doc = doc + "The MISP threat sharing platform is a free and open source software helping information sharing of threat intelligence including cyber security indicators, financial fraud or counter-terrorism information. The MISP project includes multiple sub-projects to support the operational requirements of analysts and improve the overall quality of information shared.\n\n"
    doc = doc + ""
    doc = "{}{}".format(doc, "\nMISP galaxy is a simple method to express a large object called cluster that can be attached to MISP events or attributes. A cluster can be composed of one or more elements. Elements are expressed as key-values. There are default vocabularies available in MISP galaxy but those can be overwritten, replaced or updated as you wish.  Existing clusters and vocabularies can be used as-is or as a template. MISP distribution can be applied to each cluster to permit a limited or broader distribution scheme.\n")
    doc = doc + "The following document is generated from the machine-readable JSON describing the https://github.com/MISP/misp-galaxy[MISP galaxy]."
    doc = doc + "\n\n"
    doc = doc + "<<<\n"
    doc = doc + dedication
    doc = doc + "<<<\n"
    doc = doc + "= MISP galaxy\n"
    return doc

def asciidoc(content=False, adoc=None, t='title',title=''):

    adoc = adoc + "\n"
    output = ""
    if t == 'title':
        output = '== ' + content
    elif t == 'info':
        output = "\n{}.\n\n{} {} {}{}.json[*this location*] {}.\n".format(content, 'NOTE: ', title, 'is a cluster galaxy available in JSON format at https://github.com/MISP/misp-galaxy/blob/master/clusters/',title.lower(),' The JSON format can be freely reused in your application or automatically enabled in https://www.github.com/MISP/MISP[MISP]')
    elif t == 'author':
        output = '\nauthors:: {}\n'.format(' - '.join(content))
    elif t == 'value':
        output = '=== ' + content
    elif t == 'description':
        output = '\n{}\n'.format(content)
    elif t == 'meta':
        if 'synonyms' in content:
            for s in content['synonyms']:
                output = "{}\n* {}\n".format(output,s)
            output = '{} is also known as:\n{}\n'.format(title,output)
        if 'refs' in content:
            output = '{}{}'.format(output,'\n.Table References\n|===\n|Links\n')
            for r in content['refs']:
                output = '{}|{}[{}]\n'.format(output, r, r)
            output = '{}{}'.format(output,'|===\n')
    adoc = adoc + output
    return adoc

adoc = ""
print (header(adoc=adoc))

for cluster in clusters:
    fullPathClusters = os.path.join(pathClusters, cluster)
    with open(fullPathClusters) as fp:
        c = json.load(fp)
    title = c['name']
    adoc = asciidoc(content=title, adoc=adoc, t='title')
    adoc = asciidoc(content=c['description'], adoc=adoc, t='info', title=title)
    if 'authors' in c:
        adoc = asciidoc(content=c['authors'], adoc=adoc, t='author', title=title)
    for v in c['values']:
        adoc = asciidoc(content=v['value'], adoc=adoc, t='value', title=title)
        if 'description' in v:
            adoc = asciidoc(content=v['description'], adoc=adoc, t='description')
        if 'meta' in v:
            adoc = asciidoc(content=v['meta'], adoc=adoc, t='meta', title=v['value'])


print (adoc)
