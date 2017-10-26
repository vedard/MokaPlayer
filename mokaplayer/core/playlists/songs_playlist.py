from mokaplayer.core.database import Song
from mokaplayer.core.playlists import AbstractPlaylist


class SongsPlaylist(AbstractPlaylist):

    @property
    def name(self):
        return "Songs"

    def collections(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        if order == self.OrderBy.DEFAULT:
            order = self.OrderBy.ARTIST

        return Song.select().order_by(*self.get_orderby_fields(order, desc))
