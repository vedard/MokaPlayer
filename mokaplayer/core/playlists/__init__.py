import enum
import peewee

from mokaplayer.core.database import Song


class AbstractPlaylist:
    """ Abstract class for a playlist
    """

    class OrderBy(enum.Enum):
        """ Enum for the different way to order a playlist
        """
        DEFAULT = enum.auto()
        ARTIST = enum.auto()
        ALBUM = enum.auto()
        TITLE = enum.auto()
        YEAR = enum.auto()
        LENGTH = enum.auto()
        ADDED = enum.auto()
        PLAYED = enum.auto()

    @property
    def name(self):
        """ Return the name of the playlist """

    def collections(self, order, desc):
        """ Return a list of songs in the specified order"""

    def get_orderby_fields(self, order, desc):
        """ Return a list of fields for a order by query
        """
        fields = []

        if order == self.OrderBy.ALBUM:
            fields = [peewee.fn.strip_articles(Song.Album),
                      Song.Discnumber, Song.Tracknumber]
        elif order == self.OrderBy.YEAR:
            fields = [Song.Year, peewee.fn.strip_articles(Song.Album),
                      Song.Discnumber, Song.Tracknumber]
        elif order == self.OrderBy.ADDED:
            fields = [-Song.Added, peewee.fn.strip_articles(Song.AlbumArtist), Song.Year,
                      peewee.fn.strip_articles(Song.Album), Song.Discnumber, Song.Tracknumber]
        elif order == self.OrderBy.TITLE:
            fields = [Song.Title]
        elif order == self.OrderBy.LENGTH:
            fields = [Song.Length]
        elif order == self.OrderBy.PLAYED:
            fields = [-Song.Played]
        else:
            fields = [peewee.fn.strip_articles(Song.AlbumArtist), Song.Year,
                      peewee.fn.strip_articles(Song.Album), Song.Discnumber, Song.Tracknumber]

        if desc and fields[0]._ordering == 'DESC':
            fields[0] = fields[0].asc()
        elif desc:
            fields[0] = -fields[0]

        return fields


from .songs_playlist import SongsPlaylist
from .m3u_playlist import M3UPlaylist
from .mostplayed_playlist import MostPlayedPlaylist
from .rarelyplayed_playlist import RarelyPlayedPlaylist
from .recentlyadded_playlist import RecentlyAddedPlaylist
from .recentlyplayed_playlist import RecentlyPlayedPlaylist
from .upnext_playlist import UpNextPlaylist
from .albums_playlist import AlbumsPlaylist
from .album_playlist import AlbumPlaylist
from .artists_playlist import ArtistsPlaylist
from .artist_playlist import ArtistPlaylist
