#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: driver.py
@time: 22/05/2018 16:12
"""


class Driver(object):

    def get(self, key):
        raise NotImplemented

    def put(self, key, value, secs=0):
        raise NotImplemented

    def increase(self, key, value=1):
        raise NotImplemented

    def decrease(self, key, value=1):
        raise NotImplemented

    def forget(self, key):
        raise NotImplemented

    def forever(self, key, value):
        raise NotImplemented

    def flush(self):
        raise NotImplemented
