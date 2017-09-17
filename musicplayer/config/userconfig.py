import os
import pathlib
import shutil
import logging
import yaml
import appdirs


class UserConfig(object):
    """Read, parse and manage the user configuration file
    """

    APPLICATION_DEFAULT_CONFIG_PATH = 'musicplayer/resources/default_user_config.yaml'

    def __init__(self, path):
        """ Create the user configuration file if not found
            Parse the user configuration file
        """
        self.path = path

        if self.get_file().exists():
            self.read()
        else:
            self.create()

    def read(self):
        """ Parse the YAML file
        """
        try:
            with open(self.get_file(), 'rt') as stream:
                self._data = yaml.load(stream)
        except:
            logging.critical('Could not load the user configuration file', exc_info=True)
    
    def save(self):
        """ Save the YAML file
        """
        try:
            with open(self.get_file(), 'wt') as stream:
                yaml.dump(self._data, stream, default_flow_style=False)
        except:
            logging.critical('Could not read the user configuration file', exc_info=True)


    def get_file(self):
        """ Return a file object of the current user configuration file
        """
        return pathlib.Path(self.path)

    def create(self):
        """ Copy the default user configuration file, then parse it
        """
        shutil.copy(self.APPLICATION_DEFAULT_CONFIG_PATH, self.get_file())
        self.read()

    def __getitem__(self, key):
        return self._data[key]
