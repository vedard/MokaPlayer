import pathlib

from mokaplayer.core.database import Song
from mokaplayer.core.playlists import AbstractPlaylist
from mokaplayer.core.m3u_parser import M3uParser


class M3UPlaylist(AbstractPlaylist):
    def __init__(self, path):
        self._parser = M3uParser(path)

    @property
    def parser(self):
        return self._parser

    @property
    def name(self):
        return self.parser.name

    def collections(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        paths = list(self.parser)
        if desc:
            paths = list(reversed(self.parser))

        playlist_folder = pathlib.Path(self.parser.location).parent
        query = Song.select().where(Song.Path << paths |
                                    Song.Path << [playlist_folder / (path) for path in paths])

        if order == self.OrderBy.DEFAULT:
            result = {x.Path: x for x in query}
            for path in paths:
                if path in result:
                    yield result[path]
                else:
                    path_abs = str(playlist_folder / (path))
                    if path_abs in result:
                        yield result[path_abs]
        else:
            for song in (query.order_by(*self.get_orderby_fields(order, desc))):
                yield song
