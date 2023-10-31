#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Used to generate naics galaxy clusters; takes naics.csv as entry
#naics.csv is extract from [2022]_NAICS_Structure.xlsx and only uses the 2022 NAICS Code and 2022 NAICS Title columns, without title.
#Note 1 : This only generate the file for the "clusters" folder
#Note 2 : The generated file needs to pass the jq_all_the_thigs.sh script to be in the corresponding information
#Note 3 : New uuids are generated on every run

import json
import csv
import uuid

galaxy={}
galaxy['description']="The North American Industry Classification System or NAICS is a classification of business establishments by type of economic activity (the process of production)."
galaxy['name']="NAICS"
galaxy['source']="North American Industry Classification System - NAICS"
galaxy['type']="naics"
galaxy['uuid']="b73ecad4-6529-4625-8c4f-ee3ef703a72a"
galaxy['version']=2022  #Change when updating
galaxy['authors']=[]
galaxy['authors'].append("Executive Office of the President Office of Management and Budget")
galaxy['category']="sector"

values = []

with open('naics.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        #Cluster creation
        cluster = {}
        cluster['value']=row[0]
        cluster['description']=row[1].strip()
        cluster['uuid']=str(uuid.uuid4())
        cluster['related']=[]

        values.append(cluster)

        #Relationsship preparation (Yes it's crappy but at least it works as intended ¯\_(ツ)_/¯)
        relationparent={}
        relationparent['tags']=[]
        relationparent['tags'].append("estimative-language:likelihood-probability=\"likely\"")
        relationparent['type']="parent-of"

        relationchild={}
        relationchild['tags']=[]
        relationchild['tags'].append("estimative-language:likelihood-probability=\"likely\"")
        relationchild['type']="child-of"

        relationsiblings={}
        relationsiblings['tags']=[]
        relationsiblings['tags'].append("estimative-language:likelihood-probability=\"likely\"")
        relationsiblings['type']="similar"

        relationsiblings2={}
        relationsiblings2['tags']=[]
        relationsiblings2['tags'].append("estimative-language:likelihood-probability=\"likely\"")
        relationsiblings2['type']="similar"

        #Building relationships
        if len(cluster['value']) > 2:               #2 digit codes have no parents
            if len(cluster['value']) == 6:          #specific case of 6 digit codes, parent have only 4 digits
                for value in values:
                    if value['value'] == cluster['value'][0:len(cluster['value'])-2]:
                        relationchild['dest-uuid']=value['uuid']
                        cluster['related'].append(relationchild)

                        relationparent['dest-uuid']=cluster['uuid']
                        value['related'].append(relationparent)
                        break

                if cluster['value'][5] == "0":      #If a 6 digit code ends with 0, it has a similar/identical 5 digit code
                    for value in values:
                        if value['value'] == cluster['value'][0:len(cluster['value'])-1]:
                            relationsiblings['dest-uuid']=value['uuid']
                            cluster['related'].append(relationsiblings)

                            relationsiblings2['dest-uuid']=cluster['uuid']
                            value['related'].append(relationsiblings2)
                            break



            else:                                   #All other cases (codes with 3 to 5 digits)
                for value in values:
                    if value['value'] == cluster['value'][0:len(cluster['value'])-1]:
                        relationchild['dest-uuid']=value['uuid']
                        cluster['related'].append(relationchild)

                        relationparent['dest-uuid']=cluster['uuid']
                        value['related'].append(relationparent)
                        break



galaxy['values']=values

tojson = json.dumps(galaxy, indent=2)
jsonFile = open("naisc_cluster.json", "w")
jsonFile.write(tojson)
jsonFile.close()
