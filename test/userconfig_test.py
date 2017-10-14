import unittest
import os
import logging
import pathlib

from mokaplayer.config import appconfig
from mokaplayer.config import userconfig

class UserConfigTest(unittest.TestCase):

    CONFIG_FILE_PATH = appconfig.Testing.USER_CONFIG_FILE

    def setUp(self):
        self.cfg = userconfig.UserConfig(self.CONFIG_FILE_PATH)

    def tearDown(self):
        os.remove(self.CONFIG_FILE_PATH)

    def test_read_invalid_file(self):
        with self.assertLogs(level=logging.CRITICAL):
            tmp = userconfig.UserConfig()
            tmp._path ='invalid/99999999/file'
            tmp.read()

    def test_save_invalid_file(self):
        with self.assertLogs(level=logging.CRITICAL):
            tmp = userconfig.UserConfig()
            tmp._path ='invalid/99999999/file'
            tmp.save()

    def test_get_file(self):
        self.assertIsInstance(self.cfg.get_file(), pathlib.Path)
        self.assertEqual(self.cfg.get_file().resolve(),
                         pathlib.Path(self.CONFIG_FILE_PATH).resolve())

    def test_create(self):
        os.remove(self.CONFIG_FILE_PATH)
        self.cfg.create()
        self.assertTrue(os.path.exists(self.CONFIG_FILE_PATH))

    def test_read(self):
        self.cfg['data'] = 1
        self.cfg.save()
        self.cfg['data'] = 3
        self.cfg.read()
        self.assertEqual(1, self.cfg['data'])

    def test_save(self):
        self.cfg['data'] = 1
        self.assertEqual(1, self.cfg['data'])

        self.cfg.save()
        self.assertEqual(1, self.cfg['data'])

        new_cfg = userconfig.UserConfig(self.CONFIG_FILE_PATH)
        self.assertEqual(1, new_cfg['data'])

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
