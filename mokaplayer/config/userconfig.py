import logging
import pathlib
import shutil

import appdirs
import pkg_resources
import yaml


def merge(d1, d2):
    for k in d2:
        if k in d1 and isinstance(d1[k], dict) and isinstance(d2[k], dict):
            merge(d1[k], d2[k])
        else:
            d1[k] = d2[k]


class UserConfig(object):
    """Read, parse and manage the user configuration file
    """

    APPLICATION_DEFAULT_CONFIG_PATH = pkg_resources.resource_filename('mokaplayer',
                                                                      'data/default_user_config.yaml')

    def __init__(self, path=None):
        """ Create the user configuration file if not found
            Parse the user configuration file
        """
        self._path = path
        self._data = {}
        if path is not None:
            if self.get_file().exists():
                self.read()
            elif path:
                self.create()

    def read(self):
        """ Parse the YAML file
        """
        try:
            with open(self.APPLICATION_DEFAULT_CONFIG_PATH, 'rt') as stream:
                self._data = yaml.load(stream)
            with open(self.get_file(), 'rt') as stream:
                merge(self._data, yaml.load(stream))
            self.save()
        except:
            logging.critical('Could not read the user configuration file', exc_info=True)

    def save(self):
        """ Save the YAML file
        """
        try:
            if self._path is not None:
                with open(self.get_file(), 'wt') as stream:
                    yaml.dump(self._data, stream, default_flow_style=False)
        except:
            logging.critical('Could not save the user configuration file', exc_info=True)

    def get_file(self):
        """ Return a file object of the current user configuration file
        """
        return pathlib.Path(self._path)

    def create(self):
        """ Copy the default user configuration file, then parse it
        """
        shutil.copy(self.APPLICATION_DEFAULT_CONFIG_PATH, self.get_file())
        self.read()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
