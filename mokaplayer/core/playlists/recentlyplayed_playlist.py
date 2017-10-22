from mokaplayer.core.playlists import AbstractPlaylist
from mokaplayer.core.database import Song


class RecentlyPlayedPlaylist(AbstractPlaylist):
    @property
    def name(self):
        return "Recently Played"

    def songs(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        field = Song.Last_played.asc() if desc else Song.Last_played.desc()
        return Song.select().order_by(field).limit(25)
