import peewee

from mokaplayer.core.database import Artist
from mokaplayer.core.playlists import AbstractPlaylist


class ArtistsPlaylist(AbstractPlaylist):

    @property
    def name(self):
        return "Artists"

    def collections(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        if order == self.OrderBy.ARTIST or order == self.OrderBy.DEFAULT:
            fields = [peewee.fn.strip_articles(Artist.Name)]

        if desc:
            fields[0] = -fields[0]

        return Artist.select().order_by(*fields)
