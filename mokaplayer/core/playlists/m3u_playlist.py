import pathlib

from mokaplayer.core.playlists import AbstractPlaylist
from mokaplayer.core.database import Song


class M3UPlaylist(AbstractPlaylist):
    def __init__(self, m3u_parser):
        self.m3u_parser = m3u_parser

    @property
    def name(self):
        return self.m3u_parser.name

    def songs(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        query = Song.select().where(Song.Path << list(self.m3u_parser) |
                                    Song.Path << [pathlib.Path(self.m3u_parser.location).parent / (x)
                                                  for x in self.m3u_parser])

        if order == self.OrderBy.DEFAULT:
            result = {x.Path: x for x in query}
            for path in self.m3u_parser:
                if path in result:
                    yield result[path]
                else:
                    path_abs = str(pathlib.Path(self.m3u_parser.location).parent / (path))
                    if path_abs in result:
                        yield result[path_abs]
        else:
            for song in (query.order_by(*self.get_orderby_fields(order, desc))):
                yield song
