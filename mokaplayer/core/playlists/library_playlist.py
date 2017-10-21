from mokaplayer.core.playlists import AbstractPlaylist
from mokaplayer.core.database import Song


class LibraryPlaylist(AbstractPlaylist):

    @property
    def name(self):
        return "Library"

    def songs(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        if order == self.OrderBy.DEFAULT:
            order = self.OrderBy.ARTIST

        return Song.select().order_by(*self.get_orderby_fields(order, desc))
