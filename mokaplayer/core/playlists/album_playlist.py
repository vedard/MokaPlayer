from mokaplayer.core.database import Album, Song
from mokaplayer.core.playlists import AbstractPlaylist


class AlbumPlaylist(AbstractPlaylist):

    def __init__(self, album=None, song_path=None):
        if album:
            self.album = album
        elif song_path:
            song = Song.get(Song.Path==song_path)
            self.album = Album.get(Album.Name==song.Album)

    @property
    def name(self):
        return self.album.Name

    def collections(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        return Song.select().where(Song.Album == self.album.Name)
