from mokaplayer.core.playlists import AbstractPlaylist
from mokaplayer.core.database import Song


class RecentlyAddedPlaylist(AbstractPlaylist):
    @property
    def name(self):
        return "Recently Added"

    def songs(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        field = Song.Added.asc() if desc else Song.Added.desc()
        return Song.select().order_by(field).limit(100)
