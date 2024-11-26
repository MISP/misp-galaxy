#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: test_redis.py
@time: 22/05/2018 18:43
"""
from unittest import TestCase
from sponge.drivers.redis import RedisDriver
from .driver import TestData


class RedisTest(TestData, TestCase):

    def setUp(self):
        self.driver = RedisDriver({})




