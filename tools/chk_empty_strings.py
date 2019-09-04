#!/usr/bin/env python3
# coding=utf-8
"""
    Tools to find empty string entries in galaxies
"""
from .chk_dup import loadjsons
import sys


if __name__ == '__main__':
    jsons = loadjsons("clusters", return_paths=True)
    retval = 0
    for clustername, djson in jsons:
        items = djson.get('values')
        for entry in items:
            name = entry.get('value')
            for key, value in entry.get('meta', {}).items():
                if isinstance(value, list):
                    if '' in value:
                        retval = 1
                        print("Empty string found in Cluster %r: values/%s/meta/%s"
                              "" % (clustername, name, key),
                              file=sys.stderr)
    sys.exit(retval)
