import peewee
from playhouse.sqlite_ext import SqliteExtDatabase

database_context = SqliteExtDatabase(peewee.SqliteDatabase(None))


@database_context.func()
def strip_articles(text):
    articles = ['le ', 'la ', 'les ', 'the ', 'a ']
    for a in articles:
        if text.lower().startswith(a):
            return text[len(a):]

    return text


from .song import Song
from .artist import Artist
from .album import Album
from .playlist import Playlist
