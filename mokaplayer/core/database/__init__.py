import peewee

database_context = peewee.SqliteDatabase(None)

from .song import Song
from .artist import Artist
from .album import Album
from .playlist import Playlist
