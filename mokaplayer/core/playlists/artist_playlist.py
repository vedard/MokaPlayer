import peewee

from mokaplayer.core.database import Artist, Song, Album
from mokaplayer.core.playlists import AbstractPlaylist, AlbumPlaylist

class ArtistPlaylist(AbstractPlaylist):

    def __init__(self, artist=None, song_path=None):
        if artist:
            self.artist = artist
        elif song_path:
            song = Song.get(Song.Path == song_path)
            self.artist = Artist.get(Artist.Name == song.AlbumArtist)


    @property
    def name(self):
        return self.artist.Name

    def collections(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        return [AlbumPlaylist(x) for x in Album.select().where(peewee.fn.lower(Album.Artist) == self.artist.Name.lower()).order_by(Album.Year)]
