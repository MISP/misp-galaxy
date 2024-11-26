#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: redis.py
@time: 22/05/2018 18:17
"""
import redis
import json
from sponge.drivers.driver import Driver


class RedisDriver(Driver):
    def __init__(self, cfg=None):
        if cfg is None:
            cfg = {}
        cfg['decode_responses'] = True
        self._redis = redis.Redis(**cfg)

    @staticmethod
    def _serialize(value):
        return json.dumps(value)

    @staticmethod
    def _unserialize(value):
        return json.loads(value)

    def get(self, key):
        val = self._redis.get(key)
        if val:
            return self._unserialize(val)
        return None

    def put(self, key, value, secs=0):
        if secs == 0:
            self.forever(key, value)
        else:
            self._redis.set(key, self._serialize(value), secs)

    def increase(self, key, value=1):
        self._redis.incrby(key, value)

    def decrease(self, key, value=1):
        self._redis.decr(key, value)

    def forget(self, key):
        self._redis.delete(key)

    def forever(self, key, value):
        self._redis.set(key, self._serialize(value))

    def flush(self):
        self._redis.flushdb()


