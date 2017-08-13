import os
import pathlib
import shutil
import logging
import yaml
import appdirs


class Configuration(object):
    """Read, parse and manage the configuration file
    """

    APPLICATION_NAME = 'MusicPlayer'
    APPLICATION_VERSION = '0.0.0.1'
    APPLICATION_CONFIG_FILE = "musicplayer.yaml"
    APPLICATION_DEFAULT_CONFIG_PATH = 'musicplayer/data/default_configuration.yaml'
    USER_DIRECTORY = appdirs.user_data_dir(APPLICATION_NAME, 
                                           version=APPLICATION_VERSION)
    CACHE_DIRECTORY = appdirs.user_cache_dir(APPLICATION_NAME, 
                                             version=APPLICATION_VERSION)

    def __init__(self):
        """ Create directory, create configuration file if not found, then parse it
        """
        os.makedirs(self.USER_DIRECTORY, exist_ok=True)
        os.makedirs(self.CACHE_DIRECTORY, exist_ok=True)

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
            logging.critical('Could not load configuration file', exc_info=True)
    
    def save(self):
        """ Save the YAML file
        """
        try:
            with open(self.get_file(), 'wt') as stream:
                yaml.dump(self._data, stream, default_flow_style=False)
        except:
            logging.critical('Could not read configuration file', exc_info=True)


    def get_file(self):
        """ Return a file object of the current configuration file
        """
        return pathlib.Path(self.USER_DIRECTORY) / self.APPLICATION_CONFIG_FILE

    def create(self):
        """ Copy the default configuration file, then parse it
        """
        shutil.copy(self.APPLICATION_DEFAULT_CONFIG_PATH, self.get_file())
        self.read()

    def __getitem__(self, key):
        return self._data[key]
