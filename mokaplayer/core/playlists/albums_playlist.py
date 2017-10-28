import peewee

from mokaplayer.core.database import Album
from mokaplayer.core.playlists import AbstractPlaylist


class AlbumsPlaylist(AbstractPlaylist):

    @property
    def name(self):
        return "Albums"

    def collections(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        if order == self.OrderBy.ARTIST or order == self.OrderBy.DEFAULT:
            fields = [peewee.fn.strip_articles(Album.Artist), Album.Year]
        elif order == self.OrderBy.ALBUM:
            fields = [peewee.fn.strip_articles(Album.Name)]
        elif order == self.OrderBy.YEAR:
            fields=[Album.Year, peewee.fn.strip_articles(Album.Artist)]

        if desc:
            fields[0] = -fields[0]

        return Album.select().order_by(*fields)
