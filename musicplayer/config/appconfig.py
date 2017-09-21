import os
import appdirs

from musicplayer.config import secret


class Default:
    APPLICATION_NAME = 'MusicPlayer'
    APPLICATION_VERSION = '2.1.0.0'
    USER_DIRECTORY = appdirs.user_data_dir(APPLICATION_NAME, version=APPLICATION_VERSION)
    CACHE_DIRECTORY = appdirs.user_cache_dir(APPLICATION_NAME, version=APPLICATION_VERSION)
    LASTFM_SECRET_API_KEY = secret.LASTFM_SECRET_API_KEY
    LOG_LEVEL = 'INFO'

    os.makedirs(USER_DIRECTORY, exist_ok=True)
    os.makedirs(CACHE_DIRECTORY, exist_ok=True)


class Developpement(Default):
    DATABASE_FILE = 'dev_database.db'
    USER_CONFIG_FILE = 'dev_config.yaml'
    PLAYER_CACHE_FILE = os.path.join(Default.CACHE_DIRECTORY, 'dev', 'player.gz' )
    ARTWORK_CACHE_DIRECTORY = os.path.join(Default.CACHE_DIRECTORY, 'dev', 'artworks' )
    LOG_LEVEL = 'DEBUG'


class Testing(Default):
    DATABASE_FILE = 'test_database.db'
    USER_CONFIG_FILE = 'test_config.yaml'
    PLAYER_CACHE_FILE = os.path.join(Default.CACHE_DIRECTORY, 'test', 'player.gz' )
    ARTWORK_CACHE_DIRECTORY = os.path.join(Default.CACHE_DIRECTORY, 'test', 'artworks' )
    LOG_LEVEL = 'INFO'


class Production(Default):
    DATABASE_FILE = os.path.join(Default.USER_DIRECTORY, 'database.db')
    USER_CONFIG_FILE = os.path.join(Default.USER_DIRECTORY, 'config.yaml')
    PLAYER_CACHE_FILE = os.path.join(Default.CACHE_DIRECTORY, 'player.gz' )
    ARTWORK_CACHE_DIRECTORY = os.path.join(Default.CACHE_DIRECTORY, 'artworks' )
    LOG_LEVEL = 'WARNING'
