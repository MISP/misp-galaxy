#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: test_cache.py
@time: 22/05/2018 21:17
"""
import random
import string
import time
from ddt import ddt, data, unpack


@ddt
class TestData(object):

    @staticmethod
    def key(length=5):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    @data(0, 1, 13423, '', 'hello', {}, {'hello': 'world'})
    def test_cache(self, value):
        self.driver.put('key', value)
        self.assertEqual(value, self.driver.get('key'))

    @data((0, 1), (1, 2), (1321, 1), ('', 2), ('hello', 2), ({}, 1), ({'hello': 'world'}, 2))
    @unpack
    def test_ttl_cache(self, value, ttl):
        key = self.key()
        self.driver.put(key, value, ttl)
        time.sleep(ttl / 2)
        self.assertEqual(value, self.driver.get(key))
        time.sleep(ttl / 2 + 1)
        self.assertEqual(None, self.driver.get(key))

    @data((0, 1), (3, 0), (-1, 1), (4, -4))
    @unpack
    def test_incr_decr(self, old, amount):
        key = self.key()
        self.driver.put(key, old)
        self.driver.increase(key, amount)
        self.assertEqual(old + amount, self.driver.get(key))
        self.driver.decrease(key, amount)
        self.assertEqual(old, self.driver.get(key))
        self.driver.decrease(key, amount)
        self.assertEqual(old - amount, self.driver.get(key))

    @data(0, 1, 13423, '', 'hello', {}, {'hello': 'world'})
    def test_forever(self, value):
        self.driver.forever('key', value)
        self.assertEqual(value, self.driver.get('key'))

    @data(0, 1, 13423, '', 'hello', {}, {'hello': 'world'})
    def test_forget(self, value):
        key = self.key()
        self.driver.put(key, value)
        self.driver.forget(key)
        self.assertEqual(None, self.driver.get(key))

    @data(0, 1, 13423, '', 'hello', {}, {'hello': 'world'})
    def test_flush(self, value):
        key = self.key()
        self.driver.put(key, value)
        self.driver.flush()
        self.assertEqual(None, self.driver.get(key))







