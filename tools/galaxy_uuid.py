#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stable UUID helpers for galaxy generators.

A cluster value's ``uuid`` is its permanent identity: MISP instances key on
it, and every ``related`` edge in every other galaxy points at it by uuid.
A generator that mints a fresh uuid on each run therefore does not
"regenerate" a cluster -- it replaces every entry with a new one and orphans
every inbound reference.

Two rules keep that from happening:

1. Never use :func:`uuid.uuid4` for a value that has a stable identity.
   Derive it with :func:`uuid.uuid5` from something that does not change
   between runs -- the entry's name, an upstream id -- and never from a
   position, index or ordering.
2. Prefer the uuid already committed for that entry. Even a well-chosen
   uuid5 seed changes if the seed is ever revised, so a generator should
   read the cluster it is about to overwrite and reuse what is there.

:func:`UuidAssigner` does both.
"""

import json
import uuid


def load_committed_cluster(path):
    """Return the parsed cluster at *path*, or ``None`` if it is not there."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return None


class UuidAssigner:
    """Assign uuids that stay put across regenerations.

    *namespace* seeds :func:`uuid.uuid5` for entries that have never been
    committed. *committed* is the existing cluster (as returned by
    :func:`load_committed_cluster`); uuids in it win over derivation.

    Synonyms are indexed too, so an upstream rename that demotes the old
    name to a synonym keeps the original uuid instead of orphaning it.
    """

    def __init__(self, namespace, committed=None):
        self.namespace = namespace
        self._by_value = {}
        self._by_synonym = {}
        self.cluster_uuid = None
        if committed:
            self.cluster_uuid = committed.get("uuid")
            for value in committed.get("values", []):
                name, existing = value.get("value"), value.get("uuid")
                if not name or not existing:
                    continue
                self._by_value[self._key(name)] = existing
                meta = value.get("meta")
                if isinstance(meta, dict):
                    for synonym in meta.get("synonyms") or []:
                        self._by_synonym.setdefault(self._key(synonym), existing)

    @staticmethod
    def _key(name):
        return str(name).strip().casefold()

    def derive(self, *parts):
        """A deterministic uuid5 for *parts* -- no lookup, no fallback."""
        return str(uuid.uuid5(self.namespace, "|".join(str(p) for p in parts)))

    def for_value(self, value, synonyms=(), seed=None):
        """The uuid for *value*.

        Returns the committed uuid if this entry (or one of its *synonyms*)
        already has one, otherwise a uuid5 derived from *seed* -- which
        defaults to *value* and must never include an index or position.
        """
        key = self._key(value)
        if key in self._by_value:
            return self._by_value[key]
        for synonym in synonyms:
            skey = self._key(synonym)
            # An upstream rename demotes the previous name to a synonym, so
            # look for it as a committed *value* as well as a committed
            # synonym -- otherwise the rename still orphans the entry.
            existing = self._by_value.get(skey) or self._by_synonym.get(skey)
            if existing:
                return existing
        return self.derive(*(seed if seed is not None else (value,)))

    def for_cluster(self, *seed):
        """The cluster's own uuid: the committed one, else derived."""
        return self.cluster_uuid or self.derive(*seed)
