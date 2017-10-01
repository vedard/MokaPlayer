import unittest

from musicplayer.config import userconfig

class UserConfigTest(unittest.TestCase):

    def test_merge(self):
        d1 = {}
        d2 = {'a': {'b': 'c'}, 'd': 1}
        result = {'a': {'b': 'c'}, 'd': 1}

        userconfig.merge(d1, d2)
        self.assertDictEqual(d1, result)

        d1 = {'a': {'b': '2'}, 'y': 3}
        d2 = {'a': {'b': 'c'}, 'd': 1}
        result = {'a': {'b': 'c'}, 'd': 1, 'y': 3}

        userconfig.merge(d1, d2)
        self.assertDictEqual(d1, result)
