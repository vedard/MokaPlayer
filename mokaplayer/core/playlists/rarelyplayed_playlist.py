from mokaplayer.core.database import Song
from mokaplayer.core.playlists import AbstractPlaylist


class RarelyPlayedPlaylist(AbstractPlaylist):
    @property
    def name(self):
        return "Rarely Played"

    def collections(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        field = Song.Played.desc() if desc else Song.Played.asc()
        return Song.select().where(Song.Played < 3).order_by(field).limit(70)
