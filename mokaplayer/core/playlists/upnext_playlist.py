from mokaplayer.core.playlists import AbstractPlaylist
from mokaplayer.core.database import Song


class UpNextPlaylist(AbstractPlaylist):
    def __init__(self, queue):
        self.queue = queue

    @property
    def name(self):
        return "Up next"

    def songs(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        result = {x.Path: x for x in Song.select()}
        for path in list(self.queue):
            if not path == self.queue.peek():
                yield result[path]
