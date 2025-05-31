#!/usr/bin/env python
# encoding: utf-8
import time
from sponge.drivers.driver import Driver

class SqliteDriver(Driver):
	def __init__(self, cfg=None):
		import sqlite3
		self._conn = sqlite3.connect(cfg['db'])
		self._conn.execute('CREATE TABLE IF NOT EXISTS sponge (key TEXT PRIMARY KEY, value TEXT, expire INTEGER)')

	def get(self, key):
		current_time = int(time.time())
		cursor = self._conn.execute("SELECT value FROM sponge WHERE key = ? AND expire > ?", (key, current_time))
		result = cursor.fetchone()
		if result is not None:
			return result[0]
		else:
			return None
	
	def put(self, key, value, secs=0):
		if secs == 0:
			self.forever(key, value)
		else:
			timestamp = int(time.time()) + secs
			self._conn.execute(
			"INSERT OR REPLACE INTO sponge (key, value, expire) VALUES (?, ?, ?)",
				(key, value, timestamp)
			)
			self._conn.commit()
	def _update_value(self, key, delta):
		cursor = self._conn.cursor()
		cursor.execute("SELECT value FROM sponge WHERE key = ?", (key,))
		result = cursor.fetchone()
		if result is None:
			return
		current_value = int(result[0])
		new_value = current_value + delta
		cursor.execute("UPDATE sponge SET value = ? WHERE key = ?", (new_value, key))
		self._conn.commit()

	def increase(self, key, value=1):
		self._update_value(key, value)

	def decrease(self, key, value=1):
		self._update_value(key, -value)

	def forget(self, key):
		self._conn.execute("DELETE FROM sponge WHERE key = ?", (key,))
		self._conn.commit()

	def forever(self, key, value):
		far_future_timestamp = int(time.time()) + 365 * 24 * 60 * 60  # One year from now
		self._conn.execute(
			"INSERT OR REPLACE INTO sponge (key, value, expire) VALUES (?, ?, ?)",
			(key, value, far_future_timestamp)
		)
		self._conn.commit()

	def flush(self):
		self._conn.execute("DELETE FROM sponge")
		self._conn.commit()