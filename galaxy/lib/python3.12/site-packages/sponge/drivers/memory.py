#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: arraydriver.py
@time: 22/05/2018 16:15
"""
import time
from sponge.drivers.driver import Driver


class MemoryDriver(Driver):

    def __init__(self, cfg=None):
        self._store = {}

    def get(self, key):
        if key in self._store and (self._store[key]['ttl'] == 0 or self._store[key]['ttl'] > time.time()):
            return self._store[key]['val']
        return None

    def put(self, key, value, secs=0):
        self._store[key] = {
            'val': value,
            'ttl': 0 if secs == 0 else time.time() + secs
        }

    def increase(self, key, value=1):
        if key in self._store:
            if self._store[key]['ttl'] == 0 or self._store[key]['ttl'] > time.time():
                self._store[key]['val'] += value
        else:
            self.put(key, value)

    def decrease(self, key, value=1):
        if key in self._store:
            if self._store[key]['ttl'] == 0 or self._store[key]['ttl'] > time.time():
                self._store[key]['val'] -= value

    def forget(self, key):
        if key in self._store:
            del self._store[key]

    def forever(self, key, value):
        self._store[key] = {
            'val': value,
            'ttl': 0
        }

    def flush(self):
        self._store = []

