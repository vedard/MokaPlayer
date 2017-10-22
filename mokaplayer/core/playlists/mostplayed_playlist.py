from mokaplayer.core.playlists import AbstractPlaylist
from mokaplayer.core.database import Song


class MostPlayedPlaylist(AbstractPlaylist):
    @property
    def name(self):
        return "Most Played"

    def songs(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        field = Song.Played.asc() if desc else Song.Played.desc()
        return Song.select().where(Song.Played > 0).order_by(field).limit(70)
