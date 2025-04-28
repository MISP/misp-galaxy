import unittest
import sqlite3
from unittest.mock import patch
import time

from sponge.drivers.sqlite import SQLiteDriver


class TestSQLiteDriver(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cfg = {'db': 'cache.db'}
        cls.driver = SQLiteDriver(cls.cfg)

    def tearDown(self):
        self.driver.flush()

    def test_put_and_get(self):
        key = 'test_key'
        value = 'test_value'
        expire_secs = 10

        self.driver.put(key, value, expire_secs)

        self.assertEqual(self.driver.get(key), value)

        # Wait for expiration and ensure value is no longer available
        time.sleep(expire_secs + 1)
        self.assertIsNone(self.driver.get(key))

    def test_increase_decrease(self):
        key = 'counter'
        initial_value = 10

        self.driver.put(key, str(initial_value))

        self.driver.increase(key)
        self.assertEqual(int(self.driver.get(key)), initial_value + 1)

        self.driver.decrease(key)
        self.assertEqual(int(self.driver.get(key)), initial_value)

    def test_forever(self):
        key = 'permanent_key'
        value = 'permanent_value'

        self.driver.forever(key, value)

        # Ensure value persists after a long wait
        time.sleep(2)
        self.assertEqual(self.driver.get(key), value)

    def test_forget(self):
        key = 'to_be_deleted'
        value = 'some_value'

        self.driver.put(key, value)
        self.assertIsNotNone(self.driver.get(key))

        self.driver.forget(key)
        self.assertIsNone(self.driver.get(key))

    def test_flush(self):
        keys = ['key1', 'key2', 'key3']
        values = ['value1', 'value2', 'value3']

        for key, value in zip(keys, values):
            self.driver.put(key, value)

        for key, value in zip(keys, values):
            self.assertEqual(self.driver.get(key), value)

        self.driver.flush()

        for key in keys:
            self.assertIsNone(self.driver.get(key))

    @patch('sqlite3.connect')
    def test_connection_error(self, mock_connect):
        mock_connect.side_effect = sqlite3.Error('Mocked connection error')

        with self.assertRaises(sqlite3.Error):
            SQLiteDriver({'db': 'cache.db'})

if __name__ == '__main__':
    unittest.main()