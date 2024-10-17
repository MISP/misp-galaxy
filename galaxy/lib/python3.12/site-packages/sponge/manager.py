#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: manager.py
@time: 22/05/2018 16:03
"""
import importlib
from sponge.drivers.driver import Driver


class CacheManager(object):
    _supported_stores = ('redis', 'memory', 'sqlite')

    def __init__(self, cfg):
        self._cfg = cfg
        self._stores = {}
        if 'default' not in cfg:
            keys = list(self._cfg.keys())
            if len(keys) > 0:
                self._cfg['default'] = keys[0]
            else:
                raise Exception('None config is not allowed for CacheManager')
        else:
            self._resolve(cfg['default'])
            self._stores['default'] = self._stores[cfg['default']]

    def store(self, name='default') -> Driver:
        '''
        :param name:
        :return: sponge.Driver
        '''
        if name in self._stores:
            return self._stores[name]
        elif name in self._supported_stores:
            if name in self._cfg:
                return self._resolve(name)
        else:
            raise Exception('Not supported driver [%s]' % name)

    def _resolve(self, name) -> Driver:
        '''
        :param name:
        :param cfg:
        :return: sponge.Driver
        '''
        if name not in self._cfg:
            raise Exception('Empty config for %s driver' % name)

        pck = importlib.import_module('sponge.drivers.%s' % name)
        driver = getattr(pck, '%sDriver' % name.capitalize())
        self._stores[name] = driver(self._cfg[name])
        return self._stores[name]
