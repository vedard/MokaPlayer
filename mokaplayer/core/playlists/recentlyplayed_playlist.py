from mokaplayer.core.database import Song
from mokaplayer.core.playlists import AbstractPlaylist


class RecentlyPlayedPlaylist(AbstractPlaylist):
    @property
    def name(self):
        return "Recently Played"

    def collections(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        field = Song.Last_played.asc() if desc else Song.Last_played.desc()
        return Song.select().where(Song.Played != 0).order_by(field).limit(25)
