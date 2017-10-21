from mokaplayer.core.playlists import AbstractPlaylist
from mokaplayer.core.database import Song


class M3UPlaylist(AbstractPlaylist):
    def __init__(self, m3u_parser):
        self.m3u_parser = m3u_parser

    @property
    def name(self):
        return self.m3u_parser.name

    def songs(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        if order == self.OrderBy.DEFAULT:
            result = {x.Path: x for x in Song.select()}
            for path in self.m3u_parser:
                yield result[path]
        else:
            for song in (Song.select()
                         .where(Song.Path << list(self.m3u_parser))
                         .order_by(*self.get_orderby_fields(order, desc))):
                yield song
