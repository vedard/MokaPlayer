import peewee

from mokaplayer.core.database import Artist
from mokaplayer.core.playlists import AbstractPlaylist


class ArtistsPlaylist(AbstractPlaylist):

    @property
    def name(self):
        return "Artists"

    def collections(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False, search=''):
        fields = [peewee.fn.strip_articles(Artist.Name)]

        if desc:
            fields[0] = -fields[0]

        query = Artist.select()
        if search:
            query = query.where(Artist.Name.regexp(search))

        return query.order_by(*fields)
