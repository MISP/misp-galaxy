#!/usr/bin/python3
import requests
import json
from bs4 import BeautifulSoup
import bs4
import uuid

# This tool is part of the MISP core project and released under the GNU Affero
# General Public License v3.0
#
# Copyright (C) 2020 Cormac Doherty
# Copyright (C) 2020 Roger Johnston
#
#
# version 0.1 - initial
# version 0.2 - fixed typo ( _curRef NOT curRef)

def _buildArticleSection(nxtSibling):
    _sectionParagraphs = []
    _nxtsib = nxtSibling

    # Headings and their content are at the same hierarchical
    # level in the html - just a sequence. This loop is bounded on
    # the next element being a <p>
    while ((_nxtsib is not None) and (_nxtsib.name == 'p')):
        # Almost every sentence, if not clause, in parapgraph
        # text is referenced/cited/footnoted.
        #
        # The following iterates through the sequence of 'tokens'
        # in the current <p>, building 'statements' composed of a
        # statement and a reference.
        #
        # so-called "clauses" and "references" are accumulated over
        # loop iterations i.e. a clause is appended to previous clauses
        # if a reference has yet to be accumulated. (implicitly -
        # references come after statements.)
        #
        # Once a 'clause' AND a 'statement' are accumulated, an encapsulating
        # 'statement' is appended to the section's list of paragraphs and
        # are reset.
        #
        _curClause = None
        _curRef = None

        for token in _nxtsib.contents:
            # References (links) are interleved within text blocks as <spans>.
            # The following control structure parses 'the next token' as
            #    - <spans> containing a link
            #    - disposable 'junk' if its <em>phasised and contains "Last update"
            #    - as relevant paragraph text to be accumulated.
            if (token.name == 'span'):
                _anchors = token.find_all('a', recursive=True)
                _anch = None
                if (len(_anchors) != 0):
                    _anch = _anchors[0]

                if (_anch is not None):
                    _curRef = _anch['href']
                else:
                    _curRef = None
            elif ((token.name != 'em') or (not ("Last updated" in token.text))):  # ignore the "last updated footer
                if (_curClause is not None):
                    if (isinstance(token, bs4.element.NavigableString)):
                        _curClause = _curClause + token
                    else:
                        _curClause = _curClause + token.text
                else:
                    # anomalous html handling
                    #  - <strong> and
                    #  - (useless) <a> tags
                    # appear in a few places
                    if ((token.name != 'strong') and
                            (token.name != 'em') and
                            (token.name != 'br') and
                            (token.name != 'sup') and
                            (token.name != 'a')):
                        _curClause = token  # this quashes them

            # Once a 'clause' AND a 'statement' are accumulated, an encapsulating
            # 'statement' is appended to the section's list of paragraphs and
            # are reset.
            if ((_curRef is not None) and (_curClause is not None)):
                statement = {}
                statement["clause"] = _curClause
                statement["ref"] = _curRef
                _sectionParagraphs.append(statement)
                _curClause = None
                _curRef = None

        # If a sequence of 'clauses' have been accumulated without finding a reference
        # create a reference-LESS statement.
        if ((_curClause is not None) and (not "Last updated" in _curClause)):
            statement = {}
            statement["clause"] = _curClause
            _sectionParagraphs.append(statement)

        _nxtsib = _nxtsib.find_next_sibling()

    return _sectionParagraphs


def _buildListSection(listContent):
    laboratories = []
    for lab in listContent.find_all('li', recursive="False"):
        _lab = {}
        _lab['name'] = lab.contents[0].replace(u'\xa0', '')

        ref = lab.find('a')
        if (ref is not None):
            _lab['ref'] = ref['href']
        else:
            _lab['ref'] = None

        laboratories.append(_lab)

    return laboratories


def _fetchArticle(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html5lib')
    _article = soup.body.find_all('article')[0]

    article = {}
    article['url'] = url
    article['name'] = _article.h1.text.replace('\n', '').strip()
    article['_name'] = _article.h2.contents[0]

    _artbody = _article.find('div', {"class": "article__copy"})

    # Risk Statement
    article['risk statement'] = _artbody.find('p').text

    article['intro'] = _buildArticleSection(_artbody.find('p').find_next_sibling())

    # Article body
    sections = []

    for _heading in _artbody.findChildren('h2'):
        _nxtSibling = _heading.find_next_sibling()

        section = {}
        section['title'] = _heading.text
        if (_nxtSibling.name == 'ul'):
            section['body'] = _buildListSection(_nxtSibling)
        else:
            section['body'] = _buildArticleSection(_nxtSibling)
        sections.append(section)

    article['sections'] = sections

    #    # Logo
    #    logo = _article.div[0].aside[0].find("div", {"class": "aside__logo"})

    _panel = _article.find("div", {"class": "aside__groups cf"})
    _paneldivs = _panel.find_all('div')

    for _paneldiv in _panel.find_all('div'):
        _title = _paneldiv.find('h3').text
        _items = []
        for _item in _paneldiv.find_all('li'):
            _anch = _item.find('a')
            if (_anch is not None):
                if ("Location" in _title):  # locations
                    _loc = {}
                    _loc['name'] = _anch.contents[0].replace('\n', '').strip()
                    _loc['ref'] = _anch['href']
                    _latlong = _anch['href'].split("=")[1]
                    _loc['lat'] = _latlong.split(",")[0]
                    _loc['long'] = _latlong.split(",")[1]
                    _items.append(_loc)
                else:
                    _items.append(_anch.text)
            else:
                _items.append(_item.text.replace('\n', '').strip())
        article[_title.lower()] = _items

    return article


def _gen_galaxy(scrape):
    base = {
        "authors": [
            "Australian Strategic Policy Institute"
        ],
        "category": "academic-institution",
        "description": "The China Defence Universities Tracker is a database of Chinese institutions engaged in military or security-related science and technology research. It was created by ASPI’s International Cyber Policy Centre.",
        "name": "China Defence Universities Tracker",
        "source": "ASPI International Cyber Policy Centre",
        "type": "china-defence-universities",
        "uuid": "d985d2eb-d6ad-4b44-9c69-44eb90095e23",
        "values": [
        ],
        "version": 1
    }

    for uni in scrape:
        new_template = template = {
            "description": "",
            "meta": {
                "refs": []
            },
            "uuid": "",
            "value": ""
        }

        new_template["uuid"] = str(uuid.uuid4())

        new_template["meta"]["refs"].append(uni["url"])

        new_template["value"] = uni["name"] + f" ({uni['_name']})"

        def _append_meta(key, meta):
            if uni.get(meta):
                values = []
                for value in uni[meta]:
                    if value != "":
                        values.append(value)
                if values:
                    new_template["meta"][key] = values

        if uni.get("intro"):
            for intro in uni["intro"]:
                new_template["description"] += intro["clause"]
            if new_template["description"] == "":
                new_template["description"] += uni["name"] + f" ({uni['_name']})"
        else:
            new_template["description"] += uni["name"] + f" ({uni['_name']})"

        if uni.get("risk"):
            if uni.get("risk") != "":
                new_template["meta"]["risk"] = uni["risk statement"]

        _append_meta("aliases", "aliases")

        _append_meta("supervising agencies", "supervising agencies")

        _append_meta("subsidiaries", "subsidiaries")

        _append_meta("topics", "topics")

        _append_meta("categories", "categories")

        if uni.get("sections"):
            labs = []
            for section in uni["sections"]:
                if section["title"] == "Major defence laboratories":
                    for lab in section["body"]:
                        if lab.get("name"):
                            if lab["name"] != "":
                                labs.append(lab["name"])
            if labs:
                new_template["meta"]["major defence laboratories"] = labs

        if uni.get("location"):
            if uni.get(uni["location"][0]["name"]) != "":
                new_template["meta"]["address"] = uni["location"][0]["name"]
            if uni.get(uni["location"][0]["lat"]) != "":
                new_template["meta"]["lat"] = uni["location"][0]["lat"]
            if uni.get(uni["location"][0]["long"]) != "":
                new_template["meta"]["long"] = uni["location"][0]["long"]

        base["values"].append(new_template)

    return base


def main():
    url = "https://unitracker.aspi.org.au"
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html5lib')

    table = soup.find_all('table')[0]  # Grab the first table
    head = None
    articles = []
    for row in table.find_all('tr'):
        if head is not None:
            colOne = row.find_all('td')[0].find_all('a')[0]['href']
            article = _fetchArticle(url + colOne)
            print("Processing: {}".format(url + colOne))
            articles.append(article)
        else:
            head = "bloop"

    galaxy = _gen_galaxy(articles)

    print(galaxy)

    with open("china-defence-universities.json", "w") as g:
        g.write(json.dumps(galaxy, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
