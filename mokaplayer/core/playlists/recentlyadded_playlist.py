import peewee
from mokaplayer.core.database import Song
from mokaplayer.core.playlists import AbstractPlaylist


class RecentlyAddedPlaylist(AbstractPlaylist):
    @property
    def name(self):
        return "Recently Added"

    def collections(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        field = [-Song.Added, peewee.fn.strip_articles(Song.AlbumArtist), Song.Year,
                 peewee.fn.strip_articles(Song.Album), Song.Discnumber, Song.Tracknumber]
        if desc:
            field[0] = Song.Added

        return Song.select().order_by(*field).limit(150)
